"use client";

import { create } from "zustand";

type UiState = {
  selectedEvidence: string | null;
  setSelectedEvidence: (value: string | null) => void;
};

export const useUiStore = create<UiState>((set) => ({
  selectedEvidence: null,
  setSelectedEvidence: (value) => set({ selectedEvidence: value })
}));
