import React from 'react'
// import logo from "./assets/x.svg";

function FiltersMenu({
    show,
    close
}) {
    return (
        <div>
            {/* <div class="w-full bg-gray-200 flex justify-center items-center"> */}
            {/* <div class="bg-gray-400 w-96 h-96 relative z-0"> */}
            {/* < div > */}
            <div class="absolute inset-0 flex justify-center items-center z-10 backdrop-blur-sm">
                <div className='flex flex-col shadow-2xl rounded-2xl'>
                    <div className='h-14 px-4 pt-4 flex flex-row justify-between bg-gray-300 border-b-2 border-black rounded-t-2xl'>
                        {/* <div className='h-full flex items-end '> */}
                        <label className='h-full pb-1 flex items-end text-2xl'>Filter Settings</label>
                        {/* </div> */}
                        <div className='h-full flex items-start'>
                            <button className='p-1 border border-gray-500 rounded-md hover:shadow-inner hover:border-gray-700' onClick={close}>
                                <svg fill="#000000" width="18px" height="18px" viewBox="0 0 256 256" id="Flat" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M202.82861,197.17188a3.99991,3.99991,0,1,1-5.65722,5.65624L128,133.65723,58.82861,202.82812a3.99991,3.99991,0,0,1-5.65722-5.65624L122.343,128,53.17139,58.82812a3.99991,3.99991,0,0,1,5.65722-5.65624L128,122.34277l69.17139-69.17089a3.99991,3.99991,0,0,1,5.65722,5.65624L133.657,128Z" />
                                </svg>
                            </button>
                        </div>
                    </div>
                    <div className='h-96 w-96 flex bg-white rounded-b-2xl'>
                        <div className='h-full w-1/3 flex flex-col bg-gray-200 rounded-bl-2xl'>
                            <button className='py-2 px-2 text-sm text-right border-b-2 border-gray-400 hover:bg-gray-300'>
                                Games
                            </button >
                            <button className='py-2 px-2 text-sm text-right border-b-2 border-gray-400 hover:bg-gray-300'>
                                Minutes
                            </button>
                            <button className='py-2 px-2 text-sm text-right border-b-2 border-gray-400 hover:bg-gray-300'>
                                Lineup
                            </button>
                        </div>
                        <div className='border-r-2 border-black'></div>
                        <div className='h-full w-2/3 '>
                            There
                        </div>
                    </div>
                </div>
            </div>
            {/* </div > */}
        </div >
    )
    {/* </div> */ }

}

export default FiltersMenu