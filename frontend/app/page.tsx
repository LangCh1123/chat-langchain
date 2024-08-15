"use client";

import { ToastContainer } from "react-toastify";
import { ChakraProvider } from "@chakra-ui/react";
import { QueryClient, QueryClientProvider } from "react-query";
import { Client } from "@langchain/langgraph-sdk";

import { ChatWindow } from "./components/ChatWindow";
import { LangGraphClientContext } from "./hooks/useLangGraphClient";

export default function Home() {
  const queryClient = new QueryClient();
  const langGraphClient = new Client({
    apiUrl: "/api/",
  });
  return (
    <LangGraphClientContext.Provider value={langGraphClient}>
      <QueryClientProvider client={queryClient}>
        <ChakraProvider>
          <ToastContainer />
          <ChatWindow />
        </ChakraProvider>
      </QueryClientProvider>
    </LangGraphClientContext.Provider>
  );
}
