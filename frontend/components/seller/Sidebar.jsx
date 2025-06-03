import React from 'react';
import Link from 'next/link';
import { assets } from '../../assets/assets';
import Image from 'next/image';
import { usePathname } from 'next/navigation';

const SideBar = () => {
  const pathname = usePathname();
  const menuItems = [
    { name: 'Add Product', path: '/seller', icon: assets.add_icon },
    {
      name: 'Product List',
      path: '/seller/product-list',
      icon: assets.product_list_icon,
    },
    { name: 'Orders', path: '/seller/orders', icon: assets.order_icon },
  ];

  return (
    <div className="md:w-64 w-16 min-h-screen bg-transparent text-white py-2 flex flex-col">
      {menuItems.map((item) => {
        const isActive = pathname === item.path;

        return (
          <Link href={item.path} key={item.name} passHref>
            <div
              className={`flex items-center py-3 px-4 gap-3 rounded-lg ${
                isActive
                  ? 'bg-gradient-to-r from-violet-400 via-violet-350 to-violet-0 text-white'
                  : 'hover:bg-gradient-to-r hover:from-violet-400 hover:via-violet-350 hover:to-violet-0 text-gray-300'
              } transition`}
            >
              <Image
                src={item.icon}
                alt={`${item.name.toLowerCase()}_icon`}
                className="w-7 h-7"
              />
              <p className="md:block hidden text-center">{item.name}</p>
            </div>
          </Link>
        );
      })}
    </div>
  );
};

export default SideBar;
