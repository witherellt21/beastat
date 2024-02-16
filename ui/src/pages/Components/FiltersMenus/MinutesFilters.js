import React, { useState } from 'react'

function MinutesFilters({
    apply
}) {
    const [selectedMinutes, setSelectedMinutes] = useState(20);
    const [query, setQuery] = useState({
        "MP": "MP > 20"
    });


    const updateQuery = () => {

    }

    const handleChange = (new_value) => {
        setSelectedMinutes(new_value);
    }

    return (
        // <div className='flex justify-center bg-red-500'>
        <div className='flex flex-col items-center'>
            <div className='py-2 font-bold'>
                Minutes Filters
            </div>
            <div className='w-2/3 py-2 border-t-2 border-black border-solid'></div>
            {/* <select value={selectedMinutes} onChange={(e) => setSelectedMinutes(e.target.value)}>
                <option>20+</option>
                <option>20+</option>
            </select> */}
            <input type='button' onClick={() => handleChange(selectedMinutes - 1)} />
            <input type='text' value={selectedMinutes} onChange={(e) => handleChange(e.target.value)} />
            <input type='button' onClick={() => handleChange(selectedMinutes + 1)} />
        </div>
        // </div>
    )
}

export default MinutesFilters