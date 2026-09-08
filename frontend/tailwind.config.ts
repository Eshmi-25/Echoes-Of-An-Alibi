import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        noir: {
          bg: "#101216",
          panel: "#18222d",
          soft: "#223142",
          text: "#f3efe3",
          amber: "#f2b54a",
          danger: "#ad3c3c"
        }
      },
      boxShadow: {
        dossier: "0 14px 40px rgba(0,0,0,0.35)"
      }
    }
  },
  plugins: []
};

export default config;
