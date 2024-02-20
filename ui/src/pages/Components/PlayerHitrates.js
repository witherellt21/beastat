import React from 'react'

function PlayerHitrates(props) {


    return (
        <div className='flex flex-col p-8 rounded-b-xl'>
            {/* <h1 className='flex-1 font-bold text-2xl'>
                Stat Hit-Rates
            </h1> */}
            {/* <div className='grid grid-rows-1 grid-flow-col gap-4 bg-red-500'>
             */}
            <div className='p-4 flex flex-row justify-center space-x-2'>
                <div
                    className={'max-w-48 min-w-32 flex flex-col flex-grow px-4 py-2 border-2 border-gray-900 rounded-lg ' + `( 
                            ${props.hitrates.AST > 50
                            ? 'bg-green-300'
                            : 'bg-red-300'
                        }
                        )`}
                >
                    <label className='text-xl'>Assists</label>
                    <div className='mt-2 flex justify-center'>
                        <div className='text-4xl border-2 border-black border-opacity-10 p-2 rounded-2xl'>
                            {props.hitrates.AST}%
                        </div>
                    </div>
                </div>

                <div
                    className={'min-w-32 max-w-48 flex flex-col flex-grow px-4 py-2 border-2 border-gray-900 rounded-lg ' + `( 
                        ${props.hitrates.TRB > 50
                            ? 'bg-green-300'
                            : 'bg-red-300'
                        }
                    )`}
                >
                    <label className='text-xl'>Rebounds</label>
                    <div className='mt-2 flex justify-center'>
                        <div className='text-4xl border-2 border-black border-opacity-10 p-2 rounded-2xl'>
                            {props.hitrates.TRB}%
                        </div>
                    </div>
                </div>

                <div
                    className={' min-w-32 max-w-48 flex flex-col flex-grow px-4 py-2 border-2 border-gray-900 rounded-lg ' + `( 
                        ${props.hitrates.THP > 50
                            ? 'bg-green-300'
                            : 'bg-red-300'
                        }
                    )`}
                >
                    <label className='text-xl'>3PM</label>
                    <div className='mt-2 flex justify-center'>
                        <div className='text-4xl border-2 border-black border-opacity-10 p-2 rounded-2xl'>
                            {props.hitrates.THP}%
                        </div>
                    </div>
                </div>
                <div
                    className={' min-w-32 max-w-48 flex flex-col flex-grow px-4 py-2 border-2 border-gray-900 rounded-lg ' + `( 
                        ${props.hitrates.PTS > 50
                            ? 'bg-green-300'
                            : 'bg-red-300'
                        }
                    )`}
                >
                    <label className='text-xl'>Points</label>
                    <div className='mt-2 flex justify-center'>
                        <div className='text-4xl border-2 border-black border-opacity-10 p-2 rounded-2xl'>
                            {props.hitrates.PTS}%
                        </div>
                    </div>
                </div>

            </div>
        </div >

    )
}

export default PlayerHitrates