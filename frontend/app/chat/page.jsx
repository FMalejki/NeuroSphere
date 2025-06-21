'use client';
import React, { useState, useRef, useEffect } from 'react';
import { useAppContext } from '@/context/AppContext';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import Image from 'next/image';
import { assets } from '@/assets/assets';
import Link from 'next/link';
import GridBackground from '@/components/GridBackground';

const Chat = () => {
  const { user } = useAppContext();
  const { getToken } = useAppContext();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [files, setFiles] = useState([]); // Changed to an array of files
  const [previewMessage, setPreviewMessage] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingConversations, setLoadingConversations] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true); // Added state for sidebar toggle
  const messagesEndRef = useRef(null);
  const [chats, setChats] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedModel, setSelectedModel] = useState('');
  const [selectedPrompts, setSelectedPrompts] = useState([]);
  const [availablePrompts, setAvailablePrompts] = useState([]);
  const [currentChat, setCurrentChat] = useState(null);
  const [chatTitle, setChatTitle] = useState('');
  const [generateImage, setGenerateImage] = useState(false);

  useEffect(() => {
    if (currentChat) {
      // Set messages from the selected chat
      const formattedMessages = currentChat.messages.map((msg, index) => ({
        id: index,
        content: msg.content,
        role: msg.role,
        timestamp: new Date(msg.timestamp),
        files: msg.files || [] // Include files if they exist
      }));
      setMessages(formattedMessages);
    }
  }, [currentChat])

useEffect(() => {
  if (user && user.id) {
    console.log("User ID available, fetching conversations:", user.id);
    fetchUserConversations();
  }
}, [user]);

  useEffect(() => {
    // Scroll to the latest message
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchUserPrompts = async () => {
    try {
      const token = await getToken(); 
      const response = await fetch(`/api/user/get-prompts`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          userId: user.id
        })
      });
      if (!response.ok) {
        throw new Error('Err.');
      }
      const data = await response.json();
      setAvailablePrompts(data.ownedProducts.filter((prompt) => prompt.id !== null));
    } catch (err) {
      console.error('Err:', err.message);
    }
  }

  const fetchUserConversations = async () => {
    if (!user || !user.id) {
      console.log("No user found, cannot fetch conversations");
      return;
    }
    
    try {
      setLoadingConversations(true);
      const token = await getToken();
      console.log("Fetching conversations for user:", user.id);
      
      const response = await fetch(`http://localhost:8000/conversations/${user.id}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      
      if (!response.ok) {
        throw new Error(`Failed to fetch conversations: ${response.status}`);
      }
      
      const data = await response.json();
      console.log(`Fetched ${data.length} conversations from API`);
      
      if (Array.isArray(data)) {
        const processedData = data.map(conv => ({
          ...conv,
          id: conv.id || String(conv._id),
          conversation_title: conv.conversation_title || `Chat ${new Date().toISOString()}`,
          messagesCount: conv.message_count || 0,
          messages: [] 
        }));
        
        processedData.sort((a, b) => {
          return b.id.localeCompare(a.id);
        });
        
        setChats(processedData);
        
        if (processedData.length > 0) {
          const firstChatId = processedData[0].id;
          console.log(`Loading messages for first chat: ${firstChatId}`);
          await fetchConversationMessages(firstChatId);
          
          const updatedChat = processedData.find(chat => chat.id === firstChatId);
          setCurrentChat(updatedChat);
        }
      } else {
        console.error("API returned non-array data:", data);
        setChats([]);
      }
    } catch (err) {
      console.error('Error fetching conversations:', err);
    } finally {
      setLoadingConversations(false);
    }
  };

  const fetchConversationMessages = async (conversationId) => {
    try {
      const token = await getToken();
      const response = await fetch(`http://localhost:8000/conversation/${conversationId}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      
      if (!response.ok) {
        throw new Error(`Failed to fetch conversation messages: ${response.status}`);
      }
      
      const data = await response.json();
      console.log(`Fetched conversation data for ${conversationId}:`, data);
      
      setChats(prevChats => {
        return prevChats.map(chat => {
          if (chat.id === conversationId) {
            return { ...chat, messages: data.messages || [] };
          }
          return chat;
        });
      });
      
      return data.messages || [];
    } catch (err) {
      console.error('Error fetching conversation messages:', err);
      return [];
    }
  };

  const handleSelectConversation = async (chat) => {
    try {
      if (!chat.messages || chat.messages.length === 0) {
        console.log(`Fetching messages for conversation: ${chat.id}`);
        const messages = await fetchConversationMessages(chat.id);
        
        const updatedChat = chats.find(c => c.id === chat.id);
        if (updatedChat) {
          setCurrentChat(updatedChat);
        }
      } else {
        console.log(`Using cached messages for conversation: ${chat.id}`);
        setCurrentChat(chat);
      }
    } catch (err) {
      console.error('Error selecting conversation:', err);
    }
  };

  const handleNewChat = async() => {
    await fetchUserPrompts()
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
      const token = await getToken();
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
          conversation_title: chatTitle || `${selectedModel} Chat`, // Use custom title or default
          parameters: {}
        }),
      });
  
      if (!response.ok) {
        throw new Error('Failed to create a new chat.');
      }
  
      const newChat = await response.json();
      console.log('A new chat has been created:', newChat);
      setChats((prev) => [newChat, ...prev]);
      setCurrentChat(newChat);
      setMessages([]);
      setIsModalOpen(false);
      setChatTitle(''); // Reset title for next time
    } catch (err) {
      console.error('Error while creating chat:', err.message);
      alert('An error occurred while creating the chat.');
    }
  };

  const MAX_FILE_SIZE = 5 * 1024 * 1024; 

  const handleFileChange = (event) => {
    const fileList = event.target.files;
    
    for (let i = 0; i < fileList.length; i++) {
      const file = fileList[i];
      
      if (file.size > MAX_FILE_SIZE) {
        alert(`File ${file.name} exceeds the maximum size of 5MB`);
        return;
      }
      
      const allowedTypes = ['image/jpeg', 'image/png', 'application/pdf', 'text/plain'];
      if (!allowedTypes.includes(file.type)) {
        alert(`File ${file.name} has an unsupported format`);
        return;
      }
    }
    
    setFiles(Array.from(fileList));
  };

const handleRemoveFile = (index) => {
  setFiles((prevFiles) => prevFiles.filter((_, i) => i !== index)); // Remove file from the list
};

const handleInputChange = (e) => {
  setInput(e.target.value);
  setPreviewMessage(e.target.value); // Update message preview
};

// Add this function to your Chat component
const convertFilesToBase64 = async (fileList) => {
  const fileObjects = [];
  
  for (const file of fileList) {
    const base64Data = await new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target.result.split(',')[1]); // Extract base64 data
      reader.readAsDataURL(file);
    });
    
    fileObjects.push({
      info: {
        name: file.name,
        type: file.type,
        size: file.size
      },
      data: base64Data
    });
  }
  
  return fileObjects;
};

const [lastRequestTime, setLastRequestTime] = useState(0);
const MIN_REQUEST_INTERVAL = 1000; // ms

const handleSendMessage = async () => {
  const now = Date.now();
  if (now - lastRequestTime < MIN_REQUEST_INTERVAL) {
    alert('Please wait before sending another message');
    return;
  }
  setLastRequestTime(now);

  const userMessage = {
    id: Date.now(),
    content: input,
    role: 'user',
    timestamp: new Date(),
  };

  setMessages((prev) => [...prev, userMessage]);
  setInput('');
  setPreviewMessage(null);
  setIsLoading(true);

  try {
    if (!user || !user.id) {
      throw new Error('User ID is missing or invalid');
    }
    
    if (!currentChat || !currentChat.id) {
      throw new Error('Conversation ID is missing or invalid');
    }

    const token = await getToken();
    
    // Convert files to base64 format expected by the backend
    const processedFiles = await convertFilesToBase64(files);
    
    // Prepare request data
    const requestData = {
      user_message: input,
      user_id: user.id,
      conversation_id: currentChat.id,
      model_id: currentChat.chosen_model || 'gemini', 
      prompt_ids: currentChat.chosen_prompts || [],
      files: processedFiles,
      generate_image: generateImage
    };
    
    console.log('Sending request with:', {
      model: requestData.model_id,
      prompt_count: requestData.prompt_ids.length, 
      file_count: processedFiles.length,
      generate_image: requestData.generate_image
    });

    const response = await fetch(`http://localhost:8000/prompt-request`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(requestData),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Server error:', errorText);
      throw new Error('Failed to send the message');
    }

    const data = await response.json();
    
    const aiResponse = data?.response?.response;
    let responseContent;

    // Handle both string and structured object responses from the backend
    if (typeof aiResponse === 'string') {
      responseContent = aiResponse;
    } else if (aiResponse?.items?.[0]?.content) {
      responseContent = aiResponse.items[0].content;
    } else {
      console.error('Invalid response format:', data);
      throw new Error('Received invalid response from server');
    }

    const botResponse = {
      id: Date.now() + 1,
      content: responseContent,
      role: 'assistant',
      timestamp: new Date(),
      isImage: generateImage,
    };

    setMessages((prev) => [...prev, botResponse]);
  } catch (err) {
    console.error('Error while sending the message:', err);
    alert('An error occurred while sending the message.');
  } 
  
  finally {
    setIsLoading(false);
    setFiles([]);
    setGenerateImage(false);
    console.log('Files after send:', files);
  }
};
const toggleSidebar = () => {
  setIsSidebarOpen((prev) => !prev); // Toggle sidebar state
};


  return (
    <div className="flex flex-col h-screen bg-transparent">
      <Navbar />

      {/* Main chat container */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left panel - chat list */}
        {isSidebarOpen && (
          <div className="w-64 bg-transparent flex flex-col h-full md:flex"> {/* Removed `hidden` */}
            <div className="p-4">
              <button
                onClick={handleNewChat}
                className="w-full flex items-center justify-center gap-2 bg-black hover:bg-black text-white py-2 px-4 rounded-md border border-violet-300"
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
            <div className="flex-1 overflow-y-auto px-2">
              <div className="text-xs text-gray-500 px-3 py-2">
                Recent conversations ({chats.length})
              </div>
              {chats.length === 0 ? (
                <div className="text-gray-500 text-center py-4">No conversations found</div>
              ) : (
                chats.map((chat) => (
                  <button
                    key={chat.id}
                    className={`w-full text-left px-3 py-2 rounded-md hover:bg-black ${
                      currentChat && currentChat.id === chat.id ? 'bg-transparent' : ''
                    } text-white/80 my-1 flex items-center gap-2`}
                    onClick={() => handleSelectConversation(chat)}
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
                    <div className="flex flex-col overflow-hidden">
                      <span className="truncate">{chat.conversation_title}</span>
                      <span className="text-xs text-gray-500 truncate">
                        {chat.chosen_model} • {chat.messages.length} messages
                      </span>
                    </div>
                  </button>
                ))
              )}
            </div>
          </div>
        )}

        {/* Main chat area */}
        <div className="flex-1 flex flex-col bg-transparent border-violet-300">
          {/* Sidebar toggle icon */}
          <div
            className={`absolute top-20 pt-2 transition-all ${
              isSidebarOpen ? 'left-70' : 'left-4'
            } z-50`}
          >
            <button
              onClick={toggleSidebar}
              className="bg-black text-white p-2 rounded-md border-violet-300 hover:bg-violet-500 transition-colors"
            >
              {isSidebarOpen ? (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth="1.5"
                  stroke="currentColor"
                  className="w-6 h-6"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              ) : (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth="1.5"
                  stroke="currentColor"
                  className="w-6 h-6"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M3.75 5.75h16.5M3.75 12h16.5M3.75 18.25h16.5"
                  />
                </svg>
              )}
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-32 pt-32 space-y-6">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center text-center text-white pt-20">
              <h1 className="text-3xl font-bold mb-2 text-violet-300 tracking-wider">NeuroSphere Chat</h1>
              <p className="text-gray-400 max-w-md">
                Start a conversation with our AI model
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
                        : 'bg-black text-white'
                    }`}
                  >
                    {msg.isImage ? (
                      <img src={msg.content} alt="Generated content" className="max-w-full rounded-md max-h-96" />
                    ) : (
                      msg.content
                    )}
                    {/* Display files if they exist */}
                    {msg.files && msg.files.length > 0 && (
                      <div className="mt-2 pt-2 border-t border-transparent">
                        {msg.files.map((file, index) => (
                          <div key={index} className="mt-1">
                            {file.type.startsWith('image/') ? (
                              <img
                                src={`data:${file.type};base64,${file.data}`}
                                alt={file.name}
                                className="max-w-full rounded-md max-h-64 mt-2"
                              />
                            ) : (
                              <div className="flex items-center gap-2 text-sm">
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                </svg>
                                <span>{file.name}</span>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
            {isLoading && (
              <div className="flex justify-start">
                <div className="max-w-[80%] p-3 rounded-lg bg-black text-white">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 rounded-full bg-black animate-bounce"></div>
                    <div
                      className="w-2 h-2 rounded-full bg-black animate-bounce"
                      style={{ animationDelay: '0.2s' }}
                    ></div>
                    <div
                      className="w-2 h-2 rounded-full bg-black animate-bounce"
                      style={{ animationDelay: '0.4s' }}
                    ></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {files.length > 0 && (
            <div className="flex gap-3 px-32 pb-2 justify-center">
              {files.map((file, idx) => (
                <div key={idx} className="flex items-center gap-1 bg-transparent rounded p-1">
                  {file.type.startsWith('image/') ? (
                    <img
                      src={URL.createObjectURL(file)}
                      alt={file.name}
                      className="w-12 h-12 object-cover rounded"
                    />
                  ) : (
                    <svg className="w-8 h-8 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  )}
                  <span className="text-xs text-white truncate max-w-[80px]">{file.name}</span>
                  <button
                    className="text-red-400 hover:text-red-600 ml-1"
                    onClick={() => handleRemoveFile(idx)}
                    title="Usuń"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}




            {/* Move the message input controls here, below the messages */}
            {currentChat && (
              <div className="flex gap-2 p-4 border-transparent border-none bg-transparent items-center sticky bottom-0 z-40 max-w-[80%] w-full mx-auto">
                <button
                  className="bg-violet-500 text-white p-2 rounded-md hover:bg-violet-600 transition-colors"
                  onClick={() => document.getElementById('file-input').click()}
                  title="Add files"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                  </svg>
                </button>
                <input
                  id="file-input"
                  type="file"
                  className="hidden"
                  multiple
                  onChange={handleFileChange}
                />
                <button
                  onClick={() => setGenerateImage(!generateImage)}
                  className={`${generateImage ? 'bg-violet-700 ring-2 ring-white' : 'bg-violet-500'} text-white p-2 rounded-md hover:bg-violet-600 transition-colors`}
                  title="Generate Image"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
                  </svg>
                </button>
                <input
                  type="text"
                  value={input}
                  onChange={handleInputChange}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder="Write a message..."
                  className="flex-1 p-3 bg-transparent text-white border border-violet-300 rounded-md focus:outline-none focus:ring-2 focus:ring-violet-500"
                  disabled={isLoading}
                />
                <button
                  onClick={handleSendMessage}
                  disabled={isLoading || (!input.trim() && files.length === 0)}
                  className="bg-violet-500 text-white px-4 py-2 rounded-md disabled:opacity-50 hover:bg-violet-600 transition-colors"
                >
                  Send
                </button>
              </div>
            )}


          {isModalOpen && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-[#121212] p-6 rounded-lg w-96 relative">
                <button
                  className="absolute top-4 right-4 text-white hover:text-gray-400"
                  onClick={() => setIsModalOpen(false)}
                  aria-label="Close"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth="1.5"
                    stroke="currentColor"
                    className="w-6 h-6"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
                <h2 className="text-white text-lg font-bold mb-4">New chat settings</h2>

                {/* Chat title input */}
                <label className="text-gray-400 block mb-2">Chat title (optional):</label>
                <input
                  type="text"
                  value={chatTitle}
                  onChange={(e) => setChatTitle(e.target.value)}
                  placeholder="New conversation"
                  className="w-full p-2 bg-[#2e2e2e] text-white rounded-md mb-4"
                />
                
                {/* Model selection */}
                <label className="text-gray-400 block mb-2">Select model:</label>
                <select
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                  className="w-full p-2 bg-[#2e2e2e] text-white rounded-md mb-4"
                >
                  <option value="">Select Model</option>
                  <option value="gemini">Gemini</option>
                  <option value="huggingface">Huggingface</option>
                  <option value="openai">ChatGPT</option>
                </select>
                
                {/* Prompt selection */}
                <label className="text-gray-400 block mb-2">Select prompts:</label>
                <div className="flex flex-col gap-2 mb-4">
                  {availablePrompts.map((prompt) => (
                    <label key={prompt.id} className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        value={prompt.id}
                        onChange={(e) => handlePromptSelection(e.target.value)}
                        className="form-checkbox text-white"
                      />
                      <span className="text-white">{prompt.title}</span>
                    </label>
                  ))}
                </div>

                <button
                  className="bg-violet-500 text-white px-4 py-2 rounded-md hover:bg-violet-600 transition-colors w-full"
                  onClick={handleCreateChat}
                >
                  Create
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
export default Chat;