import React from "react";
import { Paper, Text, Title } from "@mantine/core";

export type UserMessage = {
  id: string;
  data: string;
  type: "user";
};

export const UserMessageComponent: React.FC<{ message: UserMessage }> = ({
  message,
}) => {
  return (
    <Paper radius="md" p="md" withBorder shadow="md" m="lg">
      <Title dir="rtl">You</Title>
      <Text dir="rtl">{message.data}</Text>
    </Paper>
  );
};
