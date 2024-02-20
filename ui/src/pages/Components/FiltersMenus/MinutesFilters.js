import React, { useState } from 'react'
import MenuTitle from './MenuTitle';

function MinutesFilters({
    setCurrentQuery,
    currentQuery
}) {
    // const [selectedMinutes, setSelectedMinutes] = useState(0);

    const handleChange = (new_value) => {
        // setSelectedMinutes(new_value);
        setCurrentQuery({
            // MP: "> " + new_value.toString()
            MP: new_value
        });
    }

    return (
        // <div className='flex justify-center bg-red-500'>
        <div>
            {/* <div className='flex flex-col items-center'> */}

            {/* <div className='w-2/3 py-2 border-t-2 border-black border-solid'></div> */}
            <MenuTitle title="Filter Minutes Played" />
            <div className='flex flex-none justify-center items-center'>
                <label htmlFor='minimum-minutes-played-input'>Minutes Played (min):</label>
                <input
                    name='minimum-minutes-played-input'
                    type='text'
                    value={currentQuery.MP}
                    onChange={(e) => handleChange(e.target.value)}
                    className='w-10 mx-1 text-center border border-black rounded-md'
                />
                {/* </div> */}
                {/* <div className='flex flex-col'>
                    <button
                        className='px-1 flex border border-black'
                        onClick={() => handleChange(selectedMinutes + 1)}
                    >
                        <svg
                            fill="#000000"
                            height="10px"
                            width="10px"
                            version="1.1"
                            id="Layer_1"
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 330 330"
                        >
                            <path id="XMLID_224_" d="M325.606,229.393l-150.004-150C172.79,76.58,168.974,75,164.996,75c-3.979,0-7.794,1.581-10.607,4.394
                l-149.996,150c-5.858,5.858-5.858,15.355,0,21.213c5.857,5.857,15.355,5.858,21.213,0l139.39-139.393l139.397,139.393
                C307.322,253.536,311.161,255,315,255c3.839,0,7.678-1.464,10.607-4.394C331.464,244.748,331.464,235.251,325.606,229.393z"/>
                        </svg>
                    </button> */}
                {/* <button
                        className='px-1 flex border border-black'
                        onClick={() => handleChange(selectedMinutes - 1)}
                    >
                        <svg
                            version="1.1"
                            id="Capa_1"
                            xmlns="http://www.w3.org/2000/svg"
                            x="0px"
                            y="0px"
                            width="10px"
                            height="10px"
                            viewBox="0 0 960 560"
                        >
                            <g id="Rounded_Rectangle_33_copy_4_1_">
                                <path d="M480,344.181L268.869,131.889c-15.756-15.859-41.3-15.859-57.054,0c-15.754,15.857-15.754,41.57,0,57.431l237.632,238.937
                c8.395,8.451,19.562,12.254,30.553,11.698c10.993,0.556,22.159-3.247,30.555-11.698l237.631-238.937
                c15.756-15.86,15.756-41.571,0-57.431s-41.299-15.859-57.051,0L480,344.181z"/>
                            </g>
                        </svg>
                    </button> */}
                {/* </div> */}
            </div>
        </div >
        // </div >
    )
}

export default MinutesFilters