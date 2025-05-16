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
  const [chats, setChats] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedModel, setSelectedModel] = useState('');
  const [selectedPrompts, setSelectedPrompts] = useState([]);
  const [availablePrompts, setAvailablePrompts] = useState([]);
  const [currentChat, setCurrentChat] = useState(null);
  useEffect(() => {
    // Pobierz rozmowy użytkownika po załadowaniu komponentu
    fetchUserConversations();
  }, []);
  useEffect(() => {
    // Przewijanie do najnowszej wiadomości
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchUserPrompts = async () => {
    try {
      const token = await getToken(); // Pobierz token użytkownika
      const response = await fetch(`http://localhost:8000/get_user_prompts/${user.id}`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (!response.ok) {
        throw new Error('Err.');
      }
      const data = await response.json();
      setAvailablePrompts(data);
    } catch (err) {
      console.error('Err:', err.message);
    }
  }

  const fetchUserConversations = async () => {
    try {
      const token = await getToken(); // Pobierz token użytkownika
      const response = await fetch(`http://localhost:8000/conversations/${user.id}`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Err.');
      }

      const data = await response.json();
      setChats(data);
    }
    catch (err) {
      console.error('Err:', err.message);
    }
  }

  const handleNewChat = () => {
    setIsModalOpen(true);
  };

  const handlePromptSelection = (prompt) => {
  setSelectedPrompts((prev) =>
    prev.includes(prompt)
      ? prev.filter((p) => p !== prompt)
      : [...prev, prompt]
  );
  };

  const handleCreateChat = async () => {
  if (!selectedModel || selectedPrompts.length === 0) {
    alert('Select model and at least one prompt!');
    return;
  }

  try {
    const token = await getToken(); // Pobierz token użytkownika
    const response = await fetch(`http://localhost:8000/conversations/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        user_id: user.id,
        chosen_model: selectedModel,
        chosen_prompts: selectedPrompts,
        parameters: []
      }),
    });

    if (!response.ok) {
      throw new Error('Nie udało się utworzyć nowego czatu.');
    }

    const newChat = await response.json();
    setChats((prev) => [newChat, ...prev]);
    setCurrentChat(newChat);
    setMessages([]);
    setIsModalOpen(false);
  } catch (err) {
    console.error('Błąd podczas tworzenia czatu:', err.message);
    alert('Wystąpił błąd podczas tworzenia czatu.');
  }
};

const handleSendMessage = async () => {
  if (!input.trim()) return;

  // Dodaj wiadomość użytkownika do listy wiadomości
  const userMessage = {
    id: Date.now(),
    content: input,
    role: 'user',
    timestamp: new Date(),
  };

  setMessages((prev) => [...prev, userMessage]);
  setInput('');
  setIsLoading(true);

  try {
    // Pobierz token użytkownika
    const token = await getToken();

    // Wyślij wiadomość do backendu
    const response = await fetch(`http://localhost:8000/prompt-request`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        prompt_ids: selectedPrompts.ids,
        model_id: selectedModel,
        user_message: input,
        user_id: user.id,
        conversation_id: currentChat.id,
      }),
    });

    if (!response.ok) {
      throw new Error('Nie udało się wysłać wiadomości.');
    }

    // Odbierz odpowiedź od backendu
    const data = await response.json();
    const botResponse = {
      id: Date.now() + 1,
      content: data.response, 
      role: 'assistant',
      timestamp: new Date(),
    };

    // Dodaj odpowiedź bota do listy wiadomości
    setMessages((prev) => [...prev, botResponse]);
  } catch (err) {
    console.error('Błąd podczas wysyłania wiadomości:', err.message);
    alert('Wystąpił błąd podczas wysyłania wiadomości.');
  } finally {
    setIsLoading(false);
  }
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
              Nowy czat
            </button>
          </div>

          {/* Lista czatów */}
          <div className="flex-1 overflow-y-auto px-2">
            <div className="text-xs text-gray-500 px-3 py-2">Dzisiaj</div>
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
                <h1 className="text-3xl font-bold mb-2 text-violet-300 tracking-wider">NeuroSphere Chat</h1>
                <p className="text-gray-400 max-w-md">
                  Rozpocznij rozmowę z naszym modelem AI
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
          {isModalOpen && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-[#121212] p-6 rounded-lg w-96">
                <h2 className="text-white text-lg font-bold mb-4">Ustawienia nowego czatu</h2>
                
                {/* Wybór modelu */}
                <label className="text-gray-400 block mb-2">Wybierz model:</label>
                <select
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                  className="w-full p-2 bg-[#2e2e2e] text-white rounded-md mb-4"
                >
                  <option value="">Wybierz model</option>
                  <option value="gemini">Gemini</option>
                  <option value="huggingface">Huggingface</option>
                  <option value="openai">ChatGPT</option>
                </select>

                {/* Wybór promptów */}
                <label className="text-gray-400 block mb-2">Wybierz prompty:</label>
                <div className="flex flex-col gap-2 mb-4">
                  {availablePrompts.map((prompt) => (
                    <label key={prompt.id} className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        value={prompt.title}
                        onChange={(e) => handlePromptSelection(e.target.value)}
                        className="form-checkbox"
                      />
                      <span className="text-white">{prompt.name}</span>
                    </label>
                  ))}
                </div>

                {/* Przyciski */}
                <div className="flex justify-end gap-2">
                  <button
                    onClick={() => setIsModalOpen(false)}
                    className="bg-gray-700 text-white px-4 py-2 rounded-md"
                  >
                    Anuluj
                  </button>
                  <button
                    onClick={handleCreateChat}
                    className="bg-violet-500 text-white px-4 py-2 rounded-md"
                  >
                    Utwórz
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Obszar wprowadzania wiadomości */}
          <div className="p-4 border-t border-gray-800 bg-[#181818]">
            <div className="flex gap-2 max-w-4xl mx-auto">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Napisz wiadomość..."
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
                  <span>Wyślij</span>
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
