import nextPlugin from "eslint-config-next";

export default [
  ...nextPlugin,
  {
    rules: {
      "@next/next/no-img-element": "off"
    }
  }
];
