/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_SUPABASE_URL?: string;
  readonly VITE_SUPABASE_PUBLISHABLE_KEY?: string;
  readonly VITE_SAPHIRA_API_BASE_URL?: string;
  readonly VITE_SAPHIRA_MODEL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
