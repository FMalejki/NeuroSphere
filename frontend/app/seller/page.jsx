'use client';
import React, { useState } from 'react';
import { assets } from '@/assets/assets';
import Image from 'next/image';
import { useAppContext } from '@/context/AppContext';
import axios from 'axios';
import { toast } from 'react-hot-toast';

const AddProduct = () => {
  const { getToken } = useAppContext();
  const [file, setFile] = useState(null);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('');
  const [price, setPrice] = useState('');
  const [offerPrice, setOfferPrice] = useState('');
  const [promptText, setPromptText] = useState('');
  const [publicKey, setPublicKey] = useState('');

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && ['image/jpeg', 'image/jpg', 'image/png'].includes(selectedFile.type)) {
      setFile(selectedFile);
    } else {
      toast.error('File must be .jpeg, .jpg, or .png');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const formData = new FormData();

    formData.append('name', name);
    formData.append('description', description);
    formData.append('category', category);
    formData.append('price', price);
    formData.append('offerPrice', offerPrice);
    formData.append('promptText', promptText);
    formData.append('publicKey', publicKey);

    if (file) {
      formData.append('image', file);
    }

    try {
      const token = await getToken();
      const { data } = await axios.post('/api/product/add', formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data',
        },
      });
      if (data.success) {
        toast.success(data.message);
        setFile(null);
        setName('');
        setDescription('');
        setCategory('');
        setPrice('');
        setOfferPrice('');
        setPromptText('');
        setPublicKey('');
      } else {
        toast.error(data.message);
      }
    } catch (error) {
      toast.error(error.response.data.message);
    }
  };

  return (
    <div className="mx-auto w-full max-w-none rounded-none bg-transparent p-4 md:rounded-2xl md:p-8 bg-[url('/path-to-grid-image.png')] bg-cover bg-center">
      <div className="text-center">
        <h2 className="text-4xl font-bold text-violet-300">
          Add Your Prompt
        </h2>
        <p className="mt-2 text-sm text-gray-400">
          Fill in the details below to add your product to the marketplace.
        </p>
      </div>
      <form className="my-8 space-y-6 w-full" onSubmit={handleSubmit}>
        <div className="flex flex-col space-y-2">
          <label className="text-sm font-medium text-gray-300" htmlFor="image">
            Prompt Image
          </label>
          <div className="flex items-center gap-3">
            {!file ? (
              <label htmlFor="image" className="cursor-pointer bg-violet-300 text-black px-4 py-2 rounded-lg hover:bg-violet-400 transition">
                Import File
                <input
                  onChange={handleFileChange}
                  type="file"
                  id="image"
                  hidden
                />
              </label>
            ) : (
              <div className="border border-none rounded w-24 h-24 flex items-center justify-center">
                <label htmlFor="image">
                  <input
                    onChange={handleFileChange}
                    type="file"
                    id="image"
                    hidden
                  />
                  <Image
                    className="cursor-pointer"
                    src={URL.createObjectURL(file)}
                    alt=""
                    width={100}
                    height={100}
                  />
                </label>
              </div>
            )}
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Image must be of type .jpeg, .jpg, or .png
          </p>
        </div>
        <div className="flex flex-col space-y-2">
          <label className="text-sm font-medium text-gray-300" htmlFor="product-name">
            Prompt Name
          </label>
          <input
            id="product-name"
            type="text"
            placeholder="Type here"
            className="outline-none py-2 px-3 rounded border border-violet-300 bg-transparent text-white focus:border-violet-400 transition"
            onChange={(e) => setName(e.target.value)}
            value={name}
            required
          />
        </div>
        <div className="flex flex-col space-y-2">
          <label className="text-sm font-medium text-gray-300" htmlFor="product-description">
            Prompt Description
          </label>
          <textarea
            id="product-description"
            rows={4}
            className="outline-none py-2 px-3 rounded border border-violet-300 bg-transparent text-white focus:border-violet-400 transition resize-none"
            placeholder="Type here"
            onChange={(e) => setDescription(e.target.value)}
            value={description}
            required
          ></textarea>
        </div>
        <div className="flex flex-col space-y-2">
          <label className="text-sm font-medium text-gray-300" htmlFor="prompt-text">
            Prompt Text
          </label>
          <textarea
            id="prompt-text"
            rows={4}
            className="outline-none py-2 px-3 rounded border border-violet-300 bg-transparent text-white focus:border-violet-400 transition resize-none"
            placeholder="Type here"
            onChange={(e) => setPromptText(e.target.value)}
            value={promptText}
            required
          ></textarea>
        </div>
        <div className="flex flex-col space-y-2">
          <label className="text-sm font-medium text-gray-300" htmlFor="publicKey">
            Your Solana Wallet Address
          </label>
          <input
            id="publicKey"
            type="text"
            placeholder="Type here"
            className="outline-none py-2 px-3 rounded border border-violet-300 bg-transparent text-white focus:border-violet-400 transition"
            onChange={(e) => setPublicKey(e.target.value)}
            value={publicKey}
            required
          />
        </div>
        <div className="flex flex-col space-y-2">
          <label className="text-sm font-medium text-gray-300" htmlFor="category">
            Category
          </label>
          <select
            id="category"
            className="outline-none py-2 px-3 rounded border border-violet-300 bg-transparent text-white focus:border-violet-400 transition"
            onChange={(e) => setCategory(e.target.value)}
            defaultValue={category}
          >
            <option value="GPT Models">GPT Models</option>
            <option value="Prompts">Prompts</option>
            <option value="Chatbots">Chatbots</option>
            <option value="Data Analysis">Data Analysis</option>
            <option value="Image Generation">Image Generation</option>
          </select>
        </div>
        <div className="flex flex-col space-y-2">
          <label className="text-sm font-medium text-gray-300" htmlFor="product-price">
            Prompt Price
          </label>
          <input
            id="product-price"
            type="number"
            placeholder="0"
            className="outline-none py-2 px-3 rounded border border-violet-300 bg-transparent text-white focus:border-violet-400 transition"
            onChange={(e) => setPrice(e.target.value)}
            value={price}
            required
          />
        </div>
        <div className="flex flex-col space-y-2">
          <label className="text-sm font-medium text-gray-300" htmlFor="offer-price">
            Offer Price
          </label>
          <input
            id="offer-price"
            type="number"
            placeholder="0"
            className="outline-none py-2 px-3 rounded border border-violet-300 bg-transparent text-white focus:border-violet-400 transition"
            onChange={(e) => setOfferPrice(e.target.value)}
            value={offerPrice}
            required
          />
        </div>
        <button
          type="submit"
          className="group/btn relative block h-10 w-full rounded-md bg-gradient-to-br from-violet-500 to-violet-700 font-medium text-white shadow-[0px_1px_0px_0px_#ffffff40_inset,0px_-1px_0px_0px_#ffffff40_inset]"
        >
          Add prompt to the marketplace →
        </button>
      </form>
    </div>
  );
};

export default AddProduct;
