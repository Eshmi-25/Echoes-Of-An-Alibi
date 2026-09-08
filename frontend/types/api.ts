export type User = {
  id: number;
  username: string;
  email: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export type CaseSummary = {
  id: number;
  slug: string;
  title: string;
};

export type CaseDetail = {
  id: number;
  slug: string;
  title: string;
  briefing: string;
  max_actions: number;
};

export type InvestigationSummary = {
  id: number;
  case_id: number;
  status: string;
  actions_remaining: number;
  created_at: string;
};

export type InvestigationDetail = {
  id: number;
  case_id: number;
  status: string;
  actions_remaining: number;
  visited_locations: string[];
  discussed_topics: string[];
};

export type LocationState = {
  location_slug: string;
  unlocked: boolean;
  searched_count: number;
};

export type SearchResponse = {
  actions_remaining: number;
  found_clues: string[];
  newly_unlocked_locations: string[];
  newly_unlocked_suspects: string[];
};

export type SuspectState = {
  suspect_slug: string;
  unlocked: boolean;
  trust: number;
  pressure: number;
  interviewed_count: number;
};

export type Clue = {
  clue_slug: string;
  title: string;
  description: string;
  location_slug: string;
  tags: string[];
};

export type Contradiction = {
  slug: string;
  title: string;
  description: string;
};

export type ChatMessage = {
  role: string;
  content: string;
  created_at: string;
  emotion: string;
  contradiction_exposed: boolean;
  unlocked_topics: string[];
  ai_debug?: Record<string, unknown>;
};

export type Note = {
  id: number;
  title: string;
  body: string;
  created_at: string;
  updated_at: string;
};

export type BoardNode = {
  id: string;
  type: string;
  label: string;
  x: number;
  y: number;
  extra: Record<string, unknown>;
};

export type BoardEdge = {
  id: string;
  source: string;
  target: string;
  label: string;
};

export type BoardPayload = {
  nodes: BoardNode[];
  edges: BoardEdge[];
};

export type Result = {
  score: number;
  ending_slug: string;
  ending_title: string;
  ending_summary: string;
  canonical_revealed: boolean;
};
