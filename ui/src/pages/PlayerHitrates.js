import React from 'react'

function PlayerHitrates(props) {


    return (
        <div className='flex flex-col p-8 bg-gray-100 rounded-b-xl'>
            {/* <h1 className='flex-1 font-bold text-2xl'>
                Stat Hit-Rates
            </h1> */}
            {/* <div className='bg-green-400'> */}
            <div className='flex justify-center space-x-6 p-4'>
                <div
                    className={'flex flex-col px-4 py-2 border-2 border-gray-900 rounded-lg ' + `( 
                        ${props.hitrates.PTS > 50
                            ? 'bg-green-300'
                            : 'bg-red-300'
                        }
                    )`}
                >
                    <label className='text-xl'>Points</label>
                    <div className='flex mt-2'>
                        <div className='text-4xl border-2 border-black border-opacity-10 p-2 rounded-2xl'>
                            {props.hitrates.PTS}%
                        </div>
                    </div>
                </div>

                {/* AST Hit % */}
                <div
                    className={'flex flex-col px-4 py-2 border-2 border-gray-900 rounded-lg ' + `( 
                        ${props.hitrates.AST > 50
                            ? 'bg-green-300'
                            : 'bg-red-300'
                        }
                    )`}
                >
                    <label className='text-xl'>Assists</label>
                    <div className='flex mt-2'>
                        <div className='text-4xl border-2 border-black border-opacity-10 p-2 rounded-2xl'>
                            {props.hitrates.AST}%
                        </div>
                    </div>
                </div>

                <div
                    className={'flex flex-col px-4 py-2 border-2 border-gray-900 rounded-lg ' + `( 
                        ${props.hitrates.TRB > 50
                            ? 'bg-green-300'
                            : 'bg-red-300'
                        }
                    )`}
                >
                    <label className='text-xl'>Rebounds</label>
                    <div className='flex mt-2'>
                        <div className='text-4xl border-2 border-black border-opacity-10 p-2 rounded-2xl'>
                            {props.hitrates.TRB}%
                        </div>
                    </div>
                </div>

                <div
                    className={'flex flex-col px-4 py-2 border-2 border-gray-900 rounded-lg ' + `( 
                        ${props.hitrates.THP > 50
                            ? 'bg-green-300'
                            : 'bg-red-300'
                        }
                    )`}
                >
                    <label className='text-xl'>3PM</label>
                    <div className='flex mt-2'>
                        <div className='text-4xl border-2 border-black border-opacity-10 p-2 rounded-2xl'>
                            {props.hitrates.THP}%
                        </div>
                    </div>
                </div>

            </div>
        </div >

    )
}

export default PlayerHitrates