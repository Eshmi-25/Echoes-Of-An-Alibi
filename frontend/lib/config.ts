export const appConfig = {
  appName: process.env.NEXT_PUBLIC_APP_NAME ?? "Echoes of the Alibi",
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api",
  enableAiDebug: process.env.NEXT_PUBLIC_ENABLE_AI_DEBUG === "true"
};
