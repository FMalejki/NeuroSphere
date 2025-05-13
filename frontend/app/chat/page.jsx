'use client';
import React, { useState, useRef, useEffect } from 'react';
import { useAppContext } from '@/context/AppContext';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import Image from 'next/image';
import { assets } from '@/assets/assets';
import Link from 'next/link';

const Chat = () => {
  const { user, getToken } = useAppContext();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const [chats, setChats] = useState([
    { id: 1, title: 'Czat 1', createdAt: new Date() },
    { id: 2, title: 'Czat 2', createdAt: new Date() },
  ]);
  const [currentChat, setCurrentChat] = useState(null);

  useEffect(() => {
    // Przewijanie do najnowszej wiadomości
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleNewChat = () => {
    const newChat = {
      id: Date.now(),
      title: 'Nowy czat',
      createdAt: new Date(),
    };
    setChats([newChat, ...chats]);
    setCurrentChat(newChat);
    setMessages([]);
  };

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    // Dodaj wiadomość użytkownika
    const userMessage = {
      id: Date.now(),
      content: input,
      role: 'user',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    // Symulacja odpowiedzi AI (tutaj można zintegrować z rzeczywistym API)
    setTimeout(() => {
      const botResponse = {
        id: Date.now() + 1,
        content: `To jest przykładowa odpowiedź na: "${input}"`,
        role: 'assistant',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, botResponse]);
      setIsLoading(false);
    }, 1000);
  };

  return (
    <div className="flex flex-col h-screen bg-black">
      <Navbar />

      {/* Główny kontener czatu */}
      <div className="flex-1 flex overflow-hidden pt-16">
        {/* Lewy panel - lista czatów */}
        <div className="w-64 bg-[#121212] border-r border-gray-800 flex flex-col h-full md:flex">
          <div className="p-4">
            <button
              onClick={handleNewChat}
              className="w-full flex items-center justify-center gap-2 bg-[#202020] hover:bg-[#282828] text-white py-2 px-4 rounded-md border border-gray-700"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
              New chat
            </button>
          </div>

          {/* Lista czatów */}
          <div className="flex-1 overflow-y-auto px-2">
            <div className="text-xs text-gray-500 px-3 py-2">Recent chats</div>
            {chats.map((chat) => (
              <button
                key={chat.id}
                className="w-full text-left px-3 py-2 rounded-md hover:bg-[#202020] text-white/80 my-1 flex items-center gap-2"
                onClick={() => setCurrentChat(chat)}
              >
                <svg
                  width="16"
                  height="16"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                  ></path>
                </svg>
                <span className="truncate">{chat.title}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Główny obszar czatu */}
        <div className="flex-1 flex flex-col bg-[#181818]">
          {/* Wiadomości */}
          <div className="flex-1 overflow-y-auto p-4 space-y-6">
            {messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center text-white">
                {/*}
                <Image 
                  src={assets.animated_logo || '/logo.png'}
                  alt="Logo"
                  width={120}
                  height={120}
                  className="mb-6"
                />
                */}
                <h1 className="text-3xl font-bold mb-2">NeuroSphere Chat</h1>
                <p className="text-gray-400 max-w-md">
                Your AI chat starts here.
                </p>
              </div>
            ) : (
              messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] p-3 rounded-lg ${
                      msg.role === 'user'
                        ? 'bg-violet-500 text-white'
                        : 'bg-[#2e2e2e] text-white'
                    }`}
                  >
                    {msg.content}
                  </div>
                </div>
              ))
            )}
            {isLoading && (
              <div className="flex justify-start">
                <div className="max-w-[80%] p-3 rounded-lg bg-[#2e2e2e] text-white">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce"></div>
                    <div
                      className="w-2 h-2 rounded-full bg-gray-400 animate-bounce"
                      style={{ animationDelay: '0.2s' }}
                    ></div>
                    <div
                      className="w-2 h-2 rounded-full bg-gray-400 animate-bounce"
                      style={{ animationDelay: '0.4s' }}
                    ></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Obszar wprowadzania wiadomości */}
          <div className="p-4 border-t border-gray-800 bg-[#181818]">
            <div className="flex gap-2 max-w-4xl mx-auto">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Type your message..."
                className="flex-1 p-3 bg-[#2e2e2e] text-white border border-gray-700 rounded-md focus:outline-none focus:ring-2 focus:ring-violet-500"
                disabled={isLoading}
              />
              <button
                onClick={handleSendMessage}
                disabled={isLoading || !input.trim()}
                className="bg-violet-500 text-white px-4 py-2 rounded-md disabled:opacity-50 hover:bg-violet-600 transition-colors"
              >
                {isLoading ? (
                  <span className="flex items-center justify-center">
                    <svg
                      className="animate-spin h-5 w-5 text-white"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      ></circle>
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                  </span>
                ) : (
                  <span>Send</span>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;
