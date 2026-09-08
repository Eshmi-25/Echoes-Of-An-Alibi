"use client";

import axios from "axios";

import { appConfig } from "@/lib/config";
import { ApiError } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth-store";
import type {
  BoardPayload,
  CaseDetail,
  CaseSummary,
  ChatMessage,
  Clue,
  Contradiction,
  InvestigationDetail,
  InvestigationSummary,
  LocationState,
  Note,
  Result,
  SearchResponse,
  SuspectState,
  TokenResponse,
  User
} from "@/types/api";

const client = axios.create({
  baseURL: appConfig.apiBaseUrl,
  timeout: 20000
});

client.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

client.interceptors.response.use(
  (res) => res,
  (error) => {
    const status = error.response?.status ?? 500;
    const detail = error.response?.data?.detail;
    throw new ApiError(detail ?? "Request failed", status);
  }
);

export const api = {
  register: async (payload: { username: string; email: string; password: string }): Promise<User> => {
    const { data } = await client.post<User>("/auth/register", payload);
    return data;
  },
  login: async (payload: { username_or_email: string; password: string }): Promise<TokenResponse> => {
    const { data } = await client.post<TokenResponse>("/auth/login", payload);
    return data;
  },
  me: async (): Promise<User> => {
    const { data } = await client.get<User>("/auth/me");
    return data;
  },
  cases: async (): Promise<CaseSummary[]> => {
    const { data } = await client.get<CaseSummary[]>("/cases");
    return data;
  },
  caseById: async (id: number): Promise<CaseDetail> => {
    const { data } = await client.get<CaseDetail>(`/cases/${id}`);
    return data;
  },
  startInvestigation: async (caseId: number): Promise<InvestigationSummary> => {
    const { data } = await client.post<InvestigationSummary>("/investigations", { case_id: caseId });
    return data;
  },
  investigations: async (): Promise<InvestigationSummary[]> => {
    const { data } = await client.get<InvestigationSummary[]>("/investigations");
    return data;
  },
  investigation: async (id: number): Promise<InvestigationDetail> => {
    const { data } = await client.get<InvestigationDetail>(`/investigations/${id}`);
    return data;
  },
  restart: async (id: number): Promise<InvestigationSummary> => {
    const { data } = await client.post<InvestigationSummary>(`/investigations/${id}/restart`);
    return data;
  },
  locations: async (id: number): Promise<LocationState[]> => {
    const { data } = await client.get<LocationState[]>(`/investigations/${id}/locations`);
    return data;
  },
  location: async (id: number, locationSlug: string): Promise<Record<string, unknown>> => {
    const { data } = await client.get<Record<string, unknown>>(`/investigations/${id}/locations/${locationSlug}`);
    return data;
  },
  searchLocation: async (id: number, locationSlug: string): Promise<SearchResponse> => {
    const { data } = await client.post<SearchResponse>(`/investigations/${id}/locations/${locationSlug}/search`);
    return data;
  },
  suspects: async (id: number): Promise<SuspectState[]> => {
    const { data } = await client.get<SuspectState[]>(`/investigations/${id}/suspects`);
    return data;
  },
  suspect: async (id: number, slug: string): Promise<Record<string, unknown>> => {
    const { data } = await client.get<Record<string, unknown>>(`/investigations/${id}/suspects/${slug}`);
    return data;
  },
  messages: async (id: number, suspectSlug: string): Promise<ChatMessage[]> => {
    const { data } = await client.get<ChatMessage[]>(`/investigations/${id}/suspects/${suspectSlug}/messages`);
    return data;
  },
  sendMessage: async (
    id: number,
    suspectSlug: string,
    payload: { message: string; topic_slug?: string; evidence_clue_slug?: string }
  ): Promise<ChatMessage> => {
    const { data } = await client.post<ChatMessage>(`/investigations/${id}/suspects/${suspectSlug}/messages`, payload);
    return data;
  },
  confront: async (id: number, suspectSlug: string, payload: { message: string; clue_slug: string }): Promise<ChatMessage> => {
    const { data } = await client.post<ChatMessage>(`/investigations/${id}/suspects/${suspectSlug}/confront`, payload);
    return data;
  },
  clues: async (id: number): Promise<Clue[]> => {
    const { data } = await client.get<Clue[]>(`/investigations/${id}/clues`);
    return data;
  },
  contradictions: async (id: number): Promise<Contradiction[]> => {
    const { data } = await client.get<Contradiction[]>(`/investigations/${id}/contradictions`);
    return data;
  },
  notes: async (id: number): Promise<Note[]> => {
    const { data } = await client.get<Note[]>(`/investigations/${id}/notes`);
    return data;
  },
  createNote: async (id: number, payload: { title: string; body: string }): Promise<Note> => {
    const { data } = await client.post<Note>(`/investigations/${id}/notes`, payload);
    return data;
  },
  updateNote: async (id: number, noteId: number, payload: { title?: string; body?: string }): Promise<Note> => {
    const { data } = await client.patch<Note>(`/investigations/${id}/notes/${noteId}`, payload);
    return data;
  },
  deleteNote: async (id: number, noteId: number): Promise<void> => {
    await client.delete(`/investigations/${id}/notes/${noteId}`);
  },
  board: async (id: number): Promise<BoardPayload> => {
    const { data } = await client.get<BoardPayload>(`/investigations/${id}/board`);
    return data;
  },
  saveBoard: async (id: number, payload: BoardPayload): Promise<BoardPayload> => {
    const { data } = await client.put<BoardPayload>(`/investigations/${id}/board`, payload);
    return data;
  },
  accuse: async (
    id: number,
    payload: { attacker_slug: string; thief_slug: string; motive: string; supporting_clues: string[]; explanation: string }
  ): Promise<Result> => {
    const { data } = await client.post<Result>(`/investigations/${id}/accusations`, payload);
    return data;
  },
  result: async (id: number): Promise<Result> => {
    const { data } = await client.get<Result>(`/investigations/${id}/result`);
    return data;
  },
  aiStatus: async (): Promise<{ enabled: boolean; provider: string; model: string }> => {
    const { data } = await client.get<{ enabled: boolean; provider: string; model: string }>("/ai/status");
    return data;
  }
};
