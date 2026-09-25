/** 应用 fetch 客户端：Orval mutator */
export const appFetch = async <T>(url: string, init?: RequestInit): Promise<T> => {
  const response = await fetch(url, init);

  if (!response.ok) {
    throw new Error(`${response.status} ${url}`);
  }

  return (await response.json()) as T;
};
