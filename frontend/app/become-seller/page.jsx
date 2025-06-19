'use client';
import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import { toast } from 'react-hot-toast';
import { useUser } from '@clerk/nextjs';

export default function BecomeSeller() {
  const router = useRouter();
  const { user, isLoaded } = useUser();
  const [isLoading, setIsLoading] = useState(false);

  // Check if the user is already a seller
  const isSeller = user?.publicMetadata?.role === 'seller';

  const handleBecomeSeller = async () => {
    if (!isLoaded || !user) {
      toast.error('You must be logged in to become a seller');
      return;
    }

    setIsLoading(true);
    try {
      const response = await axios.post('/api/user/set-role');
      if (response.data.success) {
        toast.success('Congratulations! You are now a seller!');
        // Refresh the user object to get the updated metadata
        await user.reload();
        // Redirect to the seller panel
        router.push('/seller');
      } else {
        toast.error(
          response.data.message || 'An error occurred while changing the role'
        );
      }
    } catch (error) {
      console.error('Error:', error);
      toast.error('An error occurred while activating the seller account');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4 bg-gray-900 text-white">
      <div className="max-w-md w-full bg-gray-800 p-8 rounded-lg shadow-lg">
        <h1 className="text-3xl font-bold mb-6 text-violet-300">
          Become a Seller
        </h1>

        {isSeller ? (
          <div>
            <p className="mb-4">
              You are already a seller! Now you can add your prompts.
            </p>
            <button
              onClick={() => router.push('/seller')}
              className="w-full bg-violet-500 py-3 rounded-lg hover:bg-violet-600 transition-colors text-white font-semibold"
            >
              Go to the seller panel
            </button>
          </div>
        ) : (
          <div>
            <p className="mb-6 text-gray-300">
              Do you want to sell your prompts on our platform? Join the group
              of sellers and gain access to tools that will help you run your
              online business.
            </p>

            <button
              onClick={handleBecomeSeller}
              disabled={isLoading}
              className={`w-full py-3 rounded-lg transition-colors text-white font-semibold ${
                isLoading
                  ? 'bg-gray-600 cursor-not-allowed'
                  : 'bg-violet-500 hover:bg-violet-600'
              }`}
            >
              {isLoading ? 'Processing...' : 'Activate seller account'}
            </button>

            <p className="mt-4 text-sm text-gray-400">
              As a seller, you will be able to add prompts, manage orders and
              develop your business.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
