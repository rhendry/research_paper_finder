import React, { useState, useEffect, useRef } from "react";
import { Container, TextInput, Button, Paper, Group } from "@mantine/core";
import { UserMessage, UserMessageComponent } from "./components/user-message";
import type { components } from "./generated/types";
import {
  ResearchMessage,
  ResearchMessageComponent,
} from "./components/research-message";
import { nanoid } from "nanoid";

type ResearchSnapshot = components["schemas"]["ResearchSnapshot"];

type Message = UserMessage | ResearchMessage;

const API_URL = "http://localhost:5000";
const END_STREAM_SENTINAL = "<<HALT>>";

function App() {
  const [inputValue, setInputValue] = useState<string>("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [generating, setGenerating] = useState<boolean>(false);
  const [messageOrder, setMessageOrder] = useState<number>(0);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);
  const handleSubmit = async () => {
    if (!inputValue.trim()) return;

    setGenerating(true);
    const newMessage: UserMessage = {
      id: nanoid(),
      data: inputValue,
      type: "user",
    };
    setMessages((currentMessages: Message[]) => [
      ...currentMessages,
      newMessage,
    ]);

    const eventSource = new EventSource(
      `${API_URL}/research/create?prompt=${encodeURIComponent(inputValue)}`
    );
    eventSource.onmessage = (event) => {
      if (event.data === END_STREAM_SENTINAL) {
        setMessageOrder(0);
        eventSource.close();
        setGenerating(false);
        return;
      }

      const researchSnapshot: ResearchSnapshot = JSON.parse(event.data);

      if (researchSnapshot.order <= messageOrder) {
        // Process only new messages
        return;
      }
      setMessageOrder(researchSnapshot.order);

      setMessages((currentMessages) => {
        const messageIndex = currentMessages.findIndex(
          (message) =>
            message.type === "research" &&
            message.id === researchSnapshot.research.id
        );

        if (messageIndex > -1) {
          // If the message exists, create a new array with the updated message
          const updatedMessages = [...currentMessages];
          const existingMessage = updatedMessages[
            messageIndex
          ] as ResearchMessage; // Type assertion
          updatedMessages[messageIndex] = {
            ...existingMessage,
            data: researchSnapshot.research,
          }; // Update the text
          return updatedMessages;
        } else {
          // If the message doesn't exist, add it as a new ApiResponseMessage
          const newMessage: ResearchMessage = {
            id: researchSnapshot.research.id,
            data: researchSnapshot.research,
            type: "research",
          };
          return [...currentMessages, newMessage];
        }
      });
    };
    eventSource.onerror = (error) => {
      console.error("EventSource failed:", error);
      setMessageOrder(0);
      setGenerating(false);
      eventSource.close();
    };

    setInputValue("");
  };

  return (
    <Container pt="lg">
      {" "}
      {/* Ensure there's space for the input at the bottom */}
      <Paper
        radius="md"
        p="md"
        style={{
          height: "calc(100vh - 120px)",
          overflowY: "auto",
          marginBottom: 20,
        }}
      >
        {messages.map((message: Message) => {
          switch (message.type) {
            case "user":
              return (
                <UserMessageComponent key={message.id} message={message} />
              );
            case "research":
              return (
                <ResearchMessageComponent key={message.id} message={message} />
              );
            default:
              return null;
          }
        })}
        <div ref={messagesEndRef} />{" "}
      </Paper>
      <div
        style={{
          position: "fixed",
          bottom: 20,
          left: "50%",
          transform: "translateX(-50%)",
          width: "33%",
        }}
      >
        <Paper shadow="xs" radius="md" p="md" withBorder>
          <Group justify="apart" style={{ alignItems: "center" }}>
            <TextInput
              placeholder="Type your message here..."
              value={inputValue}
              onChange={(event: React.ChangeEvent<HTMLInputElement>) =>
                setInputValue(event.currentTarget.value)
              }
              onKeyDown={(event: React.KeyboardEvent<HTMLInputElement>) =>
                event.key === "Enter" && handleSubmit()
              }
              style={{ flexGrow: 1, border: "none", boxShadow: "none" }} // Adjust styling as needed
            />
            <Button onClick={handleSubmit} disabled={generating}>
              Send
            </Button>
          </Group>
        </Paper>
      </div>
    </Container>
  );
}

export default App;
