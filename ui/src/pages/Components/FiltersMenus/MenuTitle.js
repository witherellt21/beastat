import { Component, useEffect, useState } from "react";
import PropTypes from 'prop-types';

const MenuTitle = ({ title }) => {
    const [titleLength, setTitleLength] = useState(10);


    useEffect(() => {
        // console.log(document.getElementById('menu-title').offsetWidth)
        setTitleLength(document.getElementById('menu-title').offsetWidth)
    }, [])


    return (
        <div>
            <div className='flex justify-end'>
                <div className='w-full pr-2 text-right bg-gradient-to-l from-gray-300 to-white py-2 font-bold' id='menu-title'>
                    {title}
                </div>
            </div>

            <div className='flex justify-end mb-2'>
                <div
                    className='h-2 pt-1 bg-gradient-to-l from-black via-gray-400 to-white'
                    style={{ width: titleLength }}
                ><div className='h-full bg-white'></div></div>
            </div>
        </div>
    )
}

export default MenuTitle
