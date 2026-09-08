"use client";

import { useEffect } from "react";

import { useAuthStore } from "@/stores/auth-store";

export function useAuthBootstrap() {
  const setToken = useAuthStore((s) => s.setToken);

  useEffect(() => {
    const token = window.localStorage.getItem("echoes_token");
    if (token) {
      setToken(token);
    }
  }, [setToken]);
}
