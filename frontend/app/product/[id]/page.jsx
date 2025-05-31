'use client';
import { useEffect, useState } from 'react';
import { assets } from '@/assets/assets';
import ProductCard from '@/components/ProductCard';
import Layout from '@/components/Layout';
import Image from 'next/image';
import { useParams } from 'next/navigation';
import Loading from '@/components/Loading';
import { useAppContext } from '@/context/AppContext';
import React from 'react';
import { handlePurchaseWithFee } from '@/models/Payments';
import TradingViewWidget from '@/components/TradingViewWidget'; // Import TradingViewWidget

const Product = () => {
  const { id } = useParams();
  const { products, router, addToCart } = useAppContext();
  const [mainImage, setMainImage] = useState(null);
  const [productData, setProductData] = useState(null);
  const { user } = useAppContext();
  const [comments, setComments] = useState([]); // State for comments
  const [showAllComments, setShowAllComments] = useState(false); // State for toggling comments visibility
  const [activeButton, setActiveButton] = useState('buy'); // Dodano stan dla aktywnego przycisku
  const [volume, setVolume] = useState(0); // Dodano stan dla wolumenu

  const fetchProductData = async () => {
    const product = products.find((product) => product._id === id);
    setProductData(product);
  };

  useEffect(() => {
    fetchProductData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id, products.length]);

  const handleAddComment = (newComment) => {
    setComments((prev) => [...prev, newComment]); // Add new comment to the list
  };

  return productData ? (
    <Layout>
      <div className="px-6 md:px-12 lg:px-20 pt-20 space-y-10">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Lewy panel - wykres TradingView */}
          <div className="col-span-2 bg-gray-900/40 backdrop-blur-sm p-6 rounded-xl border border-blue-500/20 h-full">
            {/* Zmieniono wysokość kontenera na `h-full`, aby dopasować do ramki "Product Data" */}
            <h2 className="text-xl font-medium text-white mb-4">Price Chart</h2>
            <div className="h-[560px]">
              {/* Wysokość wykresu pozostawiono bez zmian */}
              <TradingViewWidget />
            </div>
          </div>

          {/* Prawy panel - dane produktu */}
          <div className="bg-gray-900/40 backdrop-blur-sm p-6 rounded-xl border border-blue-500/20">
            <div className="flex items-start justify-between mb-4">
              {/* Zdjęcie w lewym górnym rogu */}
              <div className="rounded-xl overflow-hidden bg-gray-800/30 border border-blue-500/20 w-[120px] h-[120px]">
                <Image
                  src={mainImage || productData.images[0]}
                  alt={productData.name}
                  className="w-full h-full object-cover"
                  width={120}
                  height={120}
                />
              </div>
              {/* Nazwa i ocena w prawym górnym rogu */}
              <div className="text-right">
                <h1 className="text-2xl font-medium text-white">{productData.name}</h1>
                <div className="flex items-center justify-end gap-2 mt-2">
                  <div className="flex items-center gap-0.5">
                    <Image
                      className="h-4 w-4"
                      src={assets.star_icon}
                      alt="star_icon"
                    />
                    <Image
                      className="h-4 w-4"
                      src={assets.star_icon}
                      alt="star_icon"
                    />
                    <Image
                      className="h-4 w-4"
                      src={assets.star_icon}
                      alt="star_icon"
                    />
                    <Image
                      className="h-4 w-4"
                      src={assets.star_icon}
                      alt="star_icon"
                    />
                    <Image
                      className="h-4 w-4"
                      src={assets.star_dull_icon}
                      alt="star_dull_icon"
                    />
                  </div>
                  <p className="text-gray-300">(4.5)</p>
                </div>
              </div>
            </div>
            {/* Reszta sekcji "Product Data" */}
            <p className="text-gray-300 mt-3">{productData.description}</p>
            <p className="text-2xl font-medium mt-6 text-white">
              {productData.offerPrice}{' '}
              <span className="text-blue-400">SOL</span>
              <span className="text-base font-normal text-gray-400 line-through ml-2">
                {productData.price} SOL
              </span>
            </p>
            <hr className="border-gray-700 my-6" />
            <div className="overflow-x-auto">
              <table className="table-auto border-collapse w-full max-w-md">
                <tbody>
                  <tr className="border-b border-gray-800">
                    <td className="text-gray-300 font-medium py-2">Type</td>
                    <td className="text-gray-400 py-2">
                      {productData.category}
                    </td>
                  </tr>
                  <tr className="border-b border-gray-800">
                    <td className="text-gray-300 font-medium py-2">
                      Transactions
                    </td>
                    <td className="text-gray-400 py-2">247</td>
                  </tr>
                  <tr>
                    <td className="text-gray-300 font-medium py-2">Rating</td>
                    <td className="text-gray-400 py-2">4.5/5 (68 reviews)</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div className="flex items-center mt-10 gap-4">
              <button
                onClick={() => setActiveButton('buy')}
                className={`w-full py-3 ${
                  activeButton === 'buy' ? 'bg-green-600 hover:bg-green-700' : 'bg-gray-600'
                } text-white transition rounded-lg`}
              >
                Buy
              </button>
              <button
                onClick={() => setActiveButton('sell')}
                className={`w-full py-3 ${
                  activeButton === 'sell' ? 'bg-red-600 hover:bg-red-700' : 'bg-gray-600'
                } text-white transition rounded-lg`}
              >
                Sell
              </button>
            </div>
            {/* Pole do wpisywania wolumenu */}
            <div className="mt-4">
              <input
                type="text"
                value={volume === 0 ? '' : volume} // if0 =empty
                onChange={(e) => {
                  const value = e.target.value;
                  if (/^\d*$/.test(value))
                  { // czy naki to cyfry
                    setVolume(Number(value));
                  }
                }}
                className="w-full p-2 border border-gray-700 rounded-lg bg-gray-800 text-white"
                placeholder="0" 
              />
            </div>
            {/* Przycisk Confirm */}
            <div className="mt-4">
              <button
                onClick={() => {
                  if (volume > 0) {
                    console.log("order:", productData);
                    console.log("amount: ", productData.offerPrice * volume);
                    console.log("seller_id: ", productData.userId);
                    console.log("user_id: ", user.id);
                    console.log("product_id: ", productData._id);
                    handlePurchaseWithFee(
                      productData.offerPrice * volume,
                      productData.userId,
                      user.id,
                      productData._id,
                      productData.name
                    );
                  }
                }}
                className={`w-full py-3 ${
                  volume > 0 ? 'bg-blue-600 hover:bg-blue-700' : 'bg-gray-600'
                } text-white transition rounded-lg`}
                disabled={volume <= 0}
              >
                Confirm
              </button>
            </div>
          </div>
        </div>

        {/* Nowa sekcja z trzema kolumnami */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-10">
          {/* Sekcja komentarzy */}
          <div className="bg-gray-900/40 backdrop-blur-sm p-6 rounded-xl border border-blue-500/20">
            <h2 className="text-xl font-medium text-white mb-4">Discussion</h2>
            <div className="space-y-4">
              {/* Wyświetlanie komentarzy */}
              {comments.slice(0, showAllComments ? comments.length : 3).map((comment, index) => (
                <div key={index} className="bg-gray-800 p-4 rounded-lg">
                  <p className="text-white">{comment}</p>
                  <div className="flex items-center gap-2 mt-2">
                    <button className="text-green-400">👍</button>
                    <button className="text-red-400">👎</button>
                    <button className="text-blue-400">Reply</button>
                  </div>
                </div>
              ))}
              {/* Przycisk "See more comments" */}
              {comments.length > 3 && !showAllComments && (
                <button
                  onClick={() => setShowAllComments(true)}
                  className="bg-blue-500 text-white px-4 py-2 rounded-lg"
                >
                  See more comments
                </button>
              )}
              {/* Pole do dodawania komentarzy */}
              <textarea
                className="w-full p-2 bg-gray-800 text-white rounded-lg"
                placeholder="Write a comment..."
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleAddComment(e.target.value);
                    e.target.value = '';
                  }
                }}
              ></textarea>
              <button
                onClick={() => {
                  const textarea = document.querySelector('textarea');
                  handleAddComment(textarea.value);
                  textarea.value = '';
                }}
                className="bg-blue-500 text-white px-4 py-2 rounded-lg"
              >
                Add Comment
              </button>
            </div>
          </div>

          {/* Sekcja transakcji */}
          <div className="bg-gray-900/40 backdrop-blur-sm p-6 rounded-xl border border-blue-500/20">
            <h2 className="text-xl font-medium text-white mb-4">Recent Transactions</h2>
            <ul className="space-y-2">
              <li className="text-white">User1 bought 2 SOL</li>
              <li className="text-white">User2 sold 1.5 SOL</li>
              <li className="text-white">User3 bought 3 SOL</li>
            </ul>
          </div>

          {/* Sekcja top holders */}
          <div className="bg-gray-900/40 backdrop-blur-sm p-6 rounded-xl border border-blue-500/20 h-[300px] overflow-y-auto">
            <h2 className="text-xl font-medium text-white mb-4">Top Holders</h2>
            <ul className="space-y-2">
              <li className="text-white">Holder1 - 10%</li>
              <li className="text-white">Holder2 - 8%</li>
              <li className="text-white">Holder3 - 5%</li>
              <li className="text-white">Holder4 - 4%</li>
              <li className="text-white">Holder5 - 3%</li>
              <li className="text-white">Holder6 - 2%</li>
              <li className="text-white">Holder7 - 2%</li>
              <li className="text-white">Holder8 - 1%</li>
              <li className="text-white">Holder9 - 1%</li>
              <li className="text-white">Holder10 - 1%</li>
            </ul>
          </div>
        </div>

        <div className="flex flex-col items-center">
          <div className="flex flex-col items-center mb-4 mt-16">
            <p className="text-3xl font-medium text-white">
              Featured <span className="font-medium text-blue-500">Models</span>
            </p>
            <div className="w-28 h-0.5 bg-blue-500 mt-2"></div>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6 mt-6 pb-14 w-full">
            {products.slice(0, 5).map((product, index) => (
              <ProductCard key={index} product={product} />
            ))}
          </div>
          <button className="px-8 py-2 mb-16 border border-blue-500/50 rounded-lg text-blue-400 hover:bg-blue-500/10 transition">
            View more
          </button>
        </div>
      </div>
    </Layout>
  ) : (
    <Loading />
  );
};

export default Product;
