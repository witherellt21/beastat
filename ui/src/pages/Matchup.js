import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import PropLines from '../tables/proplines/PropLines';
import PlayerHitrates from './PlayerHitrates';
import Gamelog from './Gamelog';
import FiltersMenu from './FiltersMenu';


function Matchup() {
    let { id } = useParams();
    let navigate = useNavigate();

    const [isLoading, setLoading] = useState(true);
    const [matchup, setMatchup] = useState({});
    const [homeAwayToggle, setHomeAwayToggle] = useState(true);
    const [homePlayerHitrates, setHomePlayerHitrates] = useState({})
    const [awayPlayerHitrates, setAwayPlayerHitrates] = useState({})
    const [displayFrame, setDisplayFrame] = useState(0)
    const [showFiltersMenu, setShowFiltersMenu] = useState(false)

    let loaded = false;

    useEffect(() => {
        axios.get(`http://localhost:3001/matchups/${id}`).then(async (response) => {
            setMatchup(response.data)

            axios.get(`http://localhost:3001/player-props/${response.data.home_player_id}/hitrates`).then(async (response) => {
                await setHomePlayerHitrates(response.data)
            }).catch((err) => {
                console.log(err);
                return null;
            });
            axios.get(`http://localhost:3001/player-props/${response.data.away_player_id}/hitrates`).then(async (response) => {
                await setAwayPlayerHitrates(response.data)
            }).catch((err) => {
                console.log(err);
                return null;
            });
            setLoading(false)

            console.log(homePlayerHitrates)
            console.log(awayPlayerHitrates)

        }).catch((err) => {
            console.log(err);
            return null;
        });

    }, [id, loaded]);

    return (
        <div>
            <div className='w-full h-screen flex flex-col'>
                {/* This div contains the buttons for toggling between Player Analyzers */}
                <div className='flex flex-row justify-center h-12 mb-6'>
                    {/* Player 1 Selector */}
                    <button
                        className={'flex-1 text-lg hover:bg-gray-200' + `( 
                            ${!homeAwayToggle
                                ? 'bg-gray-100 border-4 border-gray-400 border-opacity-10 hover:bg-gray-200'
                                : 'bg-gray-100 border-2 border-gray-300 border-opacity-80 shadow-gray-400 shadow-inner hover:bg-gray-200'
                            }
                        )`}
                        onClick={() => {
                            if (!homeAwayToggle) {
                                setHomeAwayToggle(true)
                            }
                        }
                        }
                    >
                        {matchup.home_player}
                    </button>
                    {/* Player 2 Selector */}
                    <button
                        className={'flex-1 text-lg hover:bg-gray-200' + `( 
                            ${homeAwayToggle
                                ? 'bg-gray-100 border-4 border-gray-400 border-opacity-10 hover:bg-gray-200'
                                : 'bg-gray-100 border-2 border-gray-300 border-opacity-80 shadow-gray-400 shadow-inner hover:bg-gray-200'
                            }
                        )`}
                        onClick={() => {
                            if (homeAwayToggle) {
                                setHomeAwayToggle(false)
                            }
                        }}
                    >
                        {matchup.away_player}
                    </button>
                </div>
                {/* 
                This div contains the Proplines for the selected player.
                It will only load after the matchup is successfully set.
                */}
                {!isLoading
                    ? (
                        <div className='flex justify-center'>
                            {homeAwayToggle
                                ? < PropLines player_id={matchup.home_player_id} />
                                : <PropLines player_id={matchup.away_player_id} />
                            }
                        </div>
                    )
                    : (
                        <div>
                            No data to display.
                        </div>
                    )
                }
                <button onClick={() => {
                    setShowFiltersMenu(!showFiltersMenu);
                }}>
                    Filters
                </button>
                {showFiltersMenu &&
                    <FiltersMenu
                        show={showFiltersMenu}
                        close={() => setShowFiltersMenu(false)}
                    />
                }
                {/* This div contains the matchup data for the selected player with the given filter selection. */}
                <div className='flex flex-none justify-center'>
                    <div className='p-8 w-4/6'>
                        <div className='flex flex-col justify-center'>
                            <div className='flex h-10'>
                                <button
                                    className={'flex flex-1 justify-center items-center border-r-0 border-2 border-gray-900 rounded-tl-md hover:bg-gray-200  bg-blue-600'
                                        // + `(${displayFrame == 0
                                        //     ? 'bg-blue-600'
                                        //     : 'bg-gray-600'
                                        // })`
                                    }
                                    onClick={() => {
                                        setDisplayFrame(0)
                                    }}
                                >
                                    Stat Hit-Rates
                                </button>
                                <div className='border-l-2 border-gray-900'></div>
                                <button
                                    className='flex flex-1 justify-center items-center border-l-0 border-2 border-gray-900 rounded-tr-md hover:bg-gray-200'
                                    onClick={() => {
                                        setDisplayFrame(1)
                                    }}
                                >
                                    Gamelogs
                                </button>
                            </div>
                            {displayFrame == 1
                                ? <div >
                                    {
                                        homeAwayToggle
                                            ? <Gamelog matchup_id={id} home_away="home" />
                                            : <Gamelog matchup_id={id} home_away="away" />
                                    }

                                </div>
                                : <div />
                            }
                            {!isLoading && displayFrame == 0
                                ? (
                                    <div className='justify-center'>
                                        {homeAwayToggle
                                            ? < PlayerHitrates hitrates={homePlayerHitrates} />
                                            : < PlayerHitrates hitrates={awayPlayerHitrates} />
                                        }
                                    </div>
                                )
                                : (
                                    <div />
                                )
                            }
                        </div>
                    </div>
                </div>
            </div>
        </div >
    )
}

export default Matchup