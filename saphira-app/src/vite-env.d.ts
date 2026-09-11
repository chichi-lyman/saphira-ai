/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_SAPHIRA_API_BASE_URL?: string;
  readonly VITE_SAPHIRA_API_KEY?: string;
  readonly VITE_SAPHIRA_MODEL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
