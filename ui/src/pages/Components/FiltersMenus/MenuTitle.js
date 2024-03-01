import { useEffect, useState } from "react";

const MenuTitle = ({ title }) => {
    const [titleLength, setTitleLength] = useState(10);


    useEffect(() => {
        setTitleLength(document.getElementById('menu-title').offsetWidth)
    }, [])


    return (
        <div>
            <div className="flex justify-end">
                <div className='w-full pr-2 text-right bg-gradient-to-l from-gray-300 to-white py-2 font-bold' id='menu-title'>
                    {title}
                </div>
            </div>
            <div className='flex justify-end'>
                <div
                    className='pt-1 bg-gradient-to-l from-black via-gray-400 to-gray-50'
                    style={{ width: titleLength }}
                ><div className='h-full bg-white'></div></div>
            </div>
        </div>
    )
}

export default MenuTitle
