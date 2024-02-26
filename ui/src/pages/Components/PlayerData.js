import React, { useEffect, useState } from 'react'
import Gamelog from './Gamelog';
import PlayerHitrates from './PlayerHitrates';
import FiltersMenu from './FiltersMenu';
import axios from 'axios';

function PlayerData({
    player_id,
    defense_rankings
}) {

    const [showFiltersMenu, setShowFiltersMenu] = useState(false);
    const [displayFrame, setDisplayFrame] = useState(0)
    const [gamelogData, setGamelogData] = useState([]);
    const [playerHitrates, setPlayerHitrates] = useState({});
    // const [defese]
    const [queryFilters, setQueryFilters] = useState({
        MP: '> 0',
        // Games: 'matchup',
        Date: '2000',
        matchups_only: false,
        limit: 100
    });

    useEffect(() => {
        let query = ''

        let i = 0
        for (const [key, value] of Object.entries(queryFilters)) {
            console.log(`${key} ${value}`);
            if (['Date', 'matchups_only', 'limit'].includes(`${key}`)) {
                continue
            }
            if (i == 0) {
                query = query + `${key} ${value}`
            } else {
                query = query + ` & ${key} ${value}`
            }
            i++
        }

        axios.get(`http://localhost:3001/player-props/${player_id}/hitrates?query=${query}&&startyear=${queryFilters.Date}&&matchups_only=${queryFilters.matchups_only}&&limit=${queryFilters.limit}`).then(async (response) => {
            console.log(response.data)
            await setPlayerHitrates(response.data)
        }).catch((err) => {
            console.log(err);
            return null;
        });

        axios.get(`http://localhost:3001/gamelogs/${player_id}?query=${query}&&startyear=${queryFilters.Date}&&matchups_only=${queryFilters.matchups_only}&&limit=${queryFilters.limit}`).then(async (response) => {
            await setGamelogData(response.data)
        });

    }, [player_id, queryFilters])

    return (
        <div className='w-full flex justify-center'>
            <div className='p-8 w-5/6 '>
                <div className='p-2 flex justify-end'>
                    <button className='p-2 flex border border-black rounded-xl' onClick={() => {
                        setShowFiltersMenu(!showFiltersMenu);
                    }}>
                        <svg
                            className="svg-icon"
                            fill="#000000"
                            width="30px"
                            height="30px"
                            viewBox="0 0 1024 1024"
                            version="1.1"
                            xmlns="http://www.w3.org/2000/svg">
                            <path
                                d="M640 288a64 64 0 1 1 0.032-128.032A64 64 0 0 1 640 288z m123.456-96c-14.304-55.04-64-96-123.456-96s-109.152 40.96-123.456 96H128v64h388.544c14.304 55.04 64 96 123.456 96s109.152-40.96 123.456-96H896V192h-132.544zM640 864a64 64 0 1 1 0.032-128.032A64 64 0 0 1 640 864m0-192c-59.456 0-109.152 40.96-123.456 96H128v64h388.544c14.304 55.04 64 96 123.456 96s109.152-40.96 123.456-96H896v-64h-132.544c-14.304-55.04-64-96-123.456-96M384 576a64 64 0 1 1 0.032-128.032A64 64 0 0 1 384 576m0-192c-59.456 0-109.152 40.96-123.456 96H128v64h132.544c14.304 55.04 64 96 123.456 96s109.152-40.96 123.456-96H896v-64H507.456c-14.304-55.04-64-96-123.456-96" fill="#181818"
                            />
                        </svg>
                    </button>
                </div>
                <div className='flex flex-col justify-center'>
                    <div className='h-10 mb-4 flex'>
                        <button
                            className={'flex flex-1 justify-center items-center border-r-0 border-2 border-gray-900 rounded-tl-md hover:bg-gray-200' + `(
                                ${displayFrame == 0 && 'bg-gray-300'}
                            )`}
                            onClick={() => {
                                setDisplayFrame(0)
                            }}
                        >
                            Stat Hit-Rates
                        </button>
                        <div className='border-l-2 border-gray-900'></div>
                        <button
                            className={'flex flex-1 justify-center items-center border-l-0 border-2 border-gray-900 rounded-tr-md hover:bg-gray-200' + `(
                                ${displayFrame == 1 && 'bg-gray-300'}
                            )`}
                            onClick={() => {
                                setDisplayFrame(1)
                            }}
                        >
                            Gamelogs
                        </button>
                    </div>
                    {displayFrame == 1
                        ? < div >
                            <Gamelog gamelogData={gamelogData} />
                        </div>
                        : <div />
                    }
                    {displayFrame == 0
                        ? (
                            <div>
                                < PlayerHitrates hitrates={playerHitrates} defense_rankings={defense_rankings} />
                            </div>
                        )
                        : (
                            <div />
                        )
                    }
                </div>
            </div>
            {showFiltersMenu &&
                <FiltersMenu
                    show={showFiltersMenu}
                    close={() => setShowFiltersMenu(false)}
                    apply={setQueryFilters}
                    queryFilters={queryFilters}
                />
            }
        </div>
    )
}

export default PlayerData