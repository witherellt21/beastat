import React, { useState, useEffect } from 'react';
import GamesFilters from './FiltersMenus/GamesFilters';
import MinutesFilters from './FiltersMenus/MinutesFilters';
import LineupFilters from './FiltersMenus/LineupFilters';

function FiltersMenu({
    show,
    close,
    apply,
    queryFilters
}) {

    const [selection, setSelection] = useState("games");
    const [showGamesMenu, setShowGamesMenu] = useState(true);
    const [showMinutesMenu, setShowMinutesMenu] = useState(false);
    const [showLineupsMenu, setShowLineupsMenu] = useState(false);
    const [currentQuery, setCurrentQuery] = useState(queryFilters)

    useEffect(() => {
        selection === "games" ? setShowGamesMenu(true) : setShowGamesMenu(false);
        selection === "minutes" ? setShowMinutesMenu(true) : setShowMinutesMenu(false);
        selection === "lineups" ? setShowLineupsMenu(true) : setShowLineupsMenu(false);
    }, [selection]);

    const setMenuSelection = async (selection) => {
        setSelection(selection)
    };

    return (
        <div>
            <div className="fixed inset-0 flex justify-center items-center z-10 backdrop-blur-sm overflow-hidden">
                <div className='flex flex-col shadow-2xl rounded-2xl'>
                    <div className='h-14 px-4 pt-4 flex flex-row justify-between bg-gradient-to-b from-gray-300 to-gray-200 border-b-2 border-black rounded-t-2xl'>
                        <label className='h-full pb-1 flex items-end text-2xl'>Filter Settings</label>
                        <div className='h-full flex items-start'>
                            <button className='p-1 border border-gray-500 rounded-md hover:shadow-inner hover:border-gray-700' onClick={close}>
                                <svg fill="#000000" width="18px" height="18px" viewBox="0 0 256 256" id="Flat" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M202.82861,197.17188a3.99991,3.99991,0,1,1-5.65722,5.65624L128,133.65723,58.82861,202.82812a3.99991,3.99991,0,0,1-5.65722-5.65624L122.343,128,53.17139,58.82812a3.99991,3.99991,0,0,1,5.65722-5.65624L128,122.34277l69.17139-69.17089a3.99991,3.99991,0,0,1,5.65722,5.65624L133.657,128Z" />
                                </svg>
                            </button>
                        </div>
                    </div>
                    <div className='h-96 flex'>
                        <div className='h-full w-1/3 flex flex-col bg-gradient-to-b from-gray-200 to-gray-100'>
                            <button
                                className='py-2 px-2 text-sm text-right border-b-2 border-gray-400 hover:bg-gray-300'
                                onClick={() => { setMenuSelection("games") }}
                            >
                                Games
                            </button >
                            <button
                                className='py-2 px-2 text-sm text-right border-b-2 border-gray-400 hover:bg-gray-300'
                                onClick={() => { setMenuSelection("minutes") }}
                            >
                                Minutes
                            </button>
                            <button
                                className='py-2 px-2 text-sm text-right border-b-2 border-gray-400 hover:bg-gray-300'
                                onClick={() => { setMenuSelection("lineups") }}
                            >
                                Lineup
                            </button>
                        </div>
                        <div className='border-black'></div>
                        <div className='h-full w-96 bg-white'>
                            {showGamesMenu && <GamesFilters setCurrentQuery={setCurrentQuery} currentQuery={currentQuery} />}
                            {showMinutesMenu && <MinutesFilters setCurrentQuery={setCurrentQuery} currentQuery={currentQuery} />}
                            {showLineupsMenu && <LineupFilters setCurrentQuery={setCurrentQuery} currentQuery={currentQuery} />}
                        </div>
                    </div>
                    <div className='h-10 px-2 flex justify-between bg-gradient-to-b from-gray-300 to-gray-100 border-t border-gray-400 rounded-b-2xl'>
                        <div className='flex items-center'>
                            <button
                                className='text-sm px-4 bg-gradient-to-b from-gray-300 to-gray-100 border border-black rounded-lg'
                                onClick={close}
                            >
                                Cancel
                            </button>
                        </div>
                        <div className='flex items-center'>
                            <button
                                className='text-sm px-4 border border-black rounded-lg bg-gradient-to-b from-indigo-400 to-indigo-200 active:shadow-xl active:from-indigo-500 active:to-indigo-300 '
                                onClick={() => {
                                    apply({ ...queryFilters, ...currentQuery });
                                    setCurrentQuery(queryFilters);
                                    close();
                                }}
                            >
                                Apply
                            </button>
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