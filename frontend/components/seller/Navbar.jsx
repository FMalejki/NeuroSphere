import React from 'react';
import { useAppContext } from '@/context/AppContext';

const Navbar = () => {
  const { router } = useAppContext();

  return (
    <div className="flex items-center px-4 md:px-8 py-3 justify-between border-none">
      {/* <Image
        onClick={() => router.push('/')}
        className="w-28 lg:w-32 cursor-pointer"
        src={assets.logo}
        alt=""
      /> */}
      <div
        onClick={() => router.push('/')}
        className="font-bold text-2xl text-violet-300 tracking-wider cursor-pointer"
      >
        NeuroSphere
      </div>
      <button
        className="bg-violet-300 text-black px-4 py-2 rounded-lg hover:bg-violet-400 transition"
        onClick={() => console.log('Logout')}
      >
        Logout
      </button>
    </div>
  );
};

export default Navbar;
