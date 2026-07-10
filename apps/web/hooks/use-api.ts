"use client";

import { useAuth } from "@clerk/nextjs";
import useSWR, { type SWRConfiguration } from "swr";

import { createApiClient } from "@/lib/api-client";

export function useAuthedFetcher<T>() {
  const { getToken } = useAuth();
  return async (path: string): Promise<T> => {
    const token = await getToken();
    return createApiClient(token).get<T>(path);
  };
}

export function useApiGet<T>(path: string | null, config?: SWRConfiguration) {
  const fetcher = useAuthedFetcher<T>();
  return useSWR<T>(path, fetcher, config);
}

export function useApiMutations() {
  const { getToken } = useAuth();
  return {
    get: async <T,>(path: string) => {
      const token = await getToken();
      return createApiClient(token).get<T>(path);
    },
    post: async <T,>(path: string, body?: unknown) => {
      const token = await getToken();
      return createApiClient(token).post<T>(path, body);
    },
    patch: async <T,>(path: string, body?: unknown) => {
      const token = await getToken();
      return createApiClient(token).patch<T>(path, body);
    },
    put: async <T,>(path: string, body?: unknown) => {
      const token = await getToken();
      return createApiClient(token).put<T>(path, body);
    },
    remove: async <T,>(path: string) => {
      const token = await getToken();
      return createApiClient(token).delete<T>(path);
    },
  };
}
