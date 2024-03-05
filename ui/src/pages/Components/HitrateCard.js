import React from 'react'

function HitrateCard({
    label,
    hitrate,
    average,
    line,
}) {
    return (
        <div
            className={' min-w-24 max-w-32 flex flex-col space-y-2 flex-grow px-2 py-1 border-2 border-gray-900 rounded-lg ' + `
        ${hitrate > 50
                    ? 'bg-green-300'
                    : 'bg-red-300'
                }
                    `}
        >
            <label className='text-lg'>{label}</label>
            {/* <hr className='black'></hr> */}
            <div className='flex justify-center'>
                <div className='text-2xl border-2 border-black border-opacity-10 p-1 rounded-2xl'>
                    {Math.round(hitrate * 10) / 10}%
                </div>
            </div>
            {/* <div className='flex w-full text-sm'> */}
            {/* <label className='text-xs'>AVG:</label> */}
            <span className='text-xs'>{average} ({Math.round((average - line) * 10) / 10})</span>
            {/* </div> */}
        </div>
    )
}

export default HitrateCard