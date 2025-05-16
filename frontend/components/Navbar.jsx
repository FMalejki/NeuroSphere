'use client';
import React from 'react';
import Link from 'next/link';
import { useAppContext } from '@/context/AppContext';
import { useClerk, UserButton } from '@clerk/nextjs';
import { CartIcon, BagIcon, HomeIcon, BoxIcon } from '@/assets/assets';

const Navbar = () => {
  const { isSeller, router, user } = useAppContext();
  const { openSignIn } = useClerk();

  return (
    <nav className="absolute top-0 left-0 right-0 z-50 flex items-center justify-between px-6 md:px-16 lg:px-32 py-5 text-white">
      <div
        className="font-bold text-2xl text-violet-300 tracking-wider cursor-pointer"
        onClick={() => router.push('/')}
      >
        NeuroSphere
      </div>
      <div className="flex items-center gap-4 lg:gap-8 max-md:hidden">
        <Link href="/" className="hover:text-blue-300 transition">
          Home
        </Link>
        <Link href="/all-products" className="hover:text-blue-300 transition">
          Shop
        </Link>
        <Link href="/chat" className="hover:text-blue-300 transition">
          Chat AI
        </Link>
        {/* TODO: Add about us page */}

        {/*}
        <Link href="/" className="hover:text-blue-300 transition">
          About Us
        </Link>
        {}
        <Link href="/" className="hover:text-blue-300 transition">
          Contact
        </Link>
            */}
        {isSeller && (
          <button
            onClick={() => router.push('/seller')}
            className="text-xs border border-white/30 hover:border-white px-6 py-2 rounded-full hover:bg-white/10 transition"
          >
            Seller mode
          </button>
        )}

        {user && !isSeller && (
          <button
            onClick={() => router.push('/become-seller')}
            className="text-xs border border-white/30 hover:border-white px-6 py-2 rounded-full hover:bg-white/10 transition"
          >
            Zostań sprzedawcą
          </button>
        )}
      </div>

      <div className="hidden md:flex items-center gap-4">
        <button
          onClick={openSignIn}
          type="button"
          className="flex items-center gap-2 hover:text-blue-300 transition"
        >
          <svg
            className="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </button>
        {user ? (
          <>
            <UserButton>
              <UserButton.MenuItems>
                <UserButton.Action
                  label="Cart"
                  labelIcon={<CartIcon />}
                  onClick={() => router.push('/cart')}
                />
              </UserButton.MenuItems>
              <UserButton.MenuItems>
                <UserButton.Action
                  label="My orders"
                  labelIcon={<BagIcon />}
                  onClick={() => router.push('/my-orders')}
                />
              </UserButton.MenuItems>
              {!isSeller && (
                <UserButton.MenuItems>
                  <UserButton.Action
                    label="Zostań sprzedawcą"
                    onClick={() => router.push('/become-seller')}
                  />
                </UserButton.MenuItems>
              )}
              <UserButton.MenuItems>
                <UserButton.Action
                  label="Chat AI"s
                  labelIcon={<BoxIcon />}
                  onClick={() => router.push('/chat')}
                />
              </UserButton.MenuItems>
            </UserButton>
          </>
        ) : (
          <button
            type="button"
            onClick={openSignIn}
            className="flex items-center gap-2 hover:text-blue-300 transition"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
              />
            </svg>
            Account
          </button>
        )}
      </div>

      <div className="flex items-center md:hidden gap-3">
        {isSeller && (
          <button
            onClick={() => router.push('/seller')}
            className="text-xs border border-white/30 px-4 py-1.5 rounded-full"
          >
            Seller mode
          </button>
        )}
        {user ? (
          <>
            <UserButton>
              <UserButton.MenuItems>
                <UserButton.Action
                  label="Home"
                  labelIcon={<HomeIcon />}
                  onClick={() => router.push('/')}
                />
              </UserButton.MenuItems>
              <UserButton.MenuItems>
                <UserButton.Action
                  label="Products"
                  labelIcon={<BoxIcon />}
                  onClick={() => router.push('/all-products')}
                />
              </UserButton.MenuItems>
              <UserButton.MenuItems>
                <UserButton.Action
                  label="Cart"
                  labelIcon={<CartIcon />}
                  onClick={() => router.push('/cart')}
                />
              </UserButton.MenuItems>
              <UserButton.MenuItems>
                <UserButton.Action
                  label="My orders"
                  labelIcon={<BagIcon />}
                  onClick={() => router.push('/my-orders')}
                />
              </UserButton.MenuItems>
              {!isSeller && (
                <UserButton.MenuItems>
                  <UserButton.Action
                    label="Zostań sprzedawcą"
                    onClick={() => router.push('/become-seller')}
                  />
                </UserButton.MenuItems>
              )}
              <UserButton.MenuItems>
                <UserButton.Action
                  label="Chat AI"
                  labelIcon={<BoxIcon />}
                  onClick={() => router.push('/chat')}
                />
              </UserButton.MenuItems>
            </UserButton>
          </>
        ) : (
          <button className="flex items-center gap-2 hover:text-blue-300 transition">
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
              ></path>
            </svg>
          </button>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
