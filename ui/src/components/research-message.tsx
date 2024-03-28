import React from "react";
import {
  Button,
  Card,
  Divider,
  Grid,
  Group,
  Paper,
  Stack,
  Text,
  ThemeIcon,
  Title,
} from "@mantine/core";
import type { components } from "../generated/types";
import { IconPdf } from "@tabler/icons-react";

type Research = components["schemas"]["Research"];
type Paper = components["schemas"]["Paper"];

export type ResearchMessage = {
  id: string;
  data: Research;
  type: "research";
};

const PaperCard: React.FC<{ paper: Paper }> = ({ paper }) => {
  return (
    <Card
      shadow="sm"
      p="lg"
      style={{
        height: "100%",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
      }}
    >
      <Group style={{ marginBottom: 5, alignItems: "center" }}>
        <Text fw={500}>
          <ThemeIcon color="blue" variant="light">
            <IconPdf size={16} />
          </ThemeIcon>{" "}
          {paper.title}
        </Text>
      </Group>
      <Divider />
      {paper.authors && (
        <Stack gap="sm" pt={10}>
          <Text size="md" fw={700}>
            Authors
          </Text>
          <Text size="sm" style={{ marginBottom: 10 }}>
            {paper.authors.join(", ")}
          </Text>
        </Stack>
      )}
      <Stack gap="sm">
        <Text size="md" fw={700}>
          Summary
        </Text>
        <Text size="sm" style={{ marginBottom: 10 }}>
          {paper.summary}
        </Text>
      </Stack>
      {paper.publisher && (
        <Stack gap="sm">
          <Text size="md" fw={700}>
            Publisher
          </Text>
          <Text size="sm" style={{ marginBottom: 10 }}>
            {paper.publisher}
          </Text>
        </Stack>
      )}
      <Button component="a" href={paper.url} target="_blank" fullWidth>
        Link
      </Button>
    </Card>
  );
};

export const ResearchMessageComponent: React.FC<{
  message: ResearchMessage;
}> = ({ message }) => {
  return (
    <Paper radius="md" p="md" withBorder shadow="md" m="lg">
      <Title style={{ paddingBottom: 10 }}>Researcher Bot</Title>
      {message.data.searches.map((search, index) => (
        <Stack key={index}>
          <Group>
            <Text key={index} size="md" fw={600}>
              Google search term: {search.query}
            </Text>
          </Group>
          <Grid gutter="lg">
            {search.papers.map((paper, index) => (
              <Grid.Col span={6} key={index}>
                {" "}
                {/* 3 cards per row */}
                <PaperCard paper={paper} />
              </Grid.Col>
            ))}
          </Grid>
          <Divider pb={10} />
        </Stack>
      ))}
    </Paper>
  );
};
