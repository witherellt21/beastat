import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import PropLines from './Components/tables/proplines/PropLines';
import PlayerData from './Components/PlayerData';


function Matchup() {
    let { id } = useParams();
    let navigate = useNavigate();

    const [isLoading, setLoading] = useState(true);
    const [matchup, setMatchup] = useState({});
    const [homeAwayToggle, setHomeAwayToggle] = useState(true);
    const [homeGamelog, setHomeGamelog] = useState([]);
    const [awayGamelog, setAwayGamelog] = useState([]);
    const [homePlayerHitrates, setHomePlayerHitrates] = useState({});
    const [awayPlayerHitrates, setAwayPlayerHitrates] = useState({});
    const [homePropLines, setHomePropLines] = useState([]);
    const [awayPropLines, setAwayPropLines] = useState([])
    const [queryFilter, setQueryFilters] = useState({});


    useEffect(() => {
        axios.get(`http://localhost:3001/matchups/${id}`).then(async (response) => {
            setMatchup(response.data)

        }).catch((err) => {
            console.log(err);
            return null;
        });

        getPlayerData(queryFilter);

    }, [id, queryFilter]);

    const getPlayerData = async (query) => {

        axios.get(`http://localhost:3001/player-props/${matchup.home_player_id}/hitrates`).then(async (response) => {
            await setHomePlayerHitrates(response.data)
        }).catch((err) => {
            console.log(err);
            return null;
        });
        axios.get(`http://localhost:3001/player-props/${matchup.away_player_id}/hitrates`).then(async (response) => {
            await setAwayPlayerHitrates(response.data)
        }).catch((err) => {
            console.log(err);
            return null;
        });
        axios.get(`http://localhost:3001/player-props/${matchup.home_player_id}`)
            .then((response) => {
                setHomePropLines(response.data)
            })
            .catch((error) => {
                console.log(error)
                return null;
            });
        axios.get(`http://localhost:3001/player-props/${matchup.away_player_id}`)
            .then((response) => {
                setAwayPropLines(response.data)
            })
            .catch((error) => {
                console.log(error)
                return null;
            });

        axios.get(`http://localhost:3001/matchups/${id}/stats/home`).then((response) => {
            setHomeGamelog(response.data)
        });
        axios.get(`http://localhost:3001/matchups/${id}/stats/home`).then((response) => {
            setAwayGamelog(response.data)
        });

        setLoading(false);
    }

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
                This div contains the all data for the selected player.
                It will only load after the matchup is successfully set.
                */}
                {!isLoading
                    ? (
                        <div className='flex flex-col justify-center '>
                            {homeAwayToggle
                                ? (
                                    <div>
                                        {/* This div represents the top row of the player data column. */}
                                        <div className='flex flex-none justify-center '>
                                            < PropLines propData={homePropLines} />
                                        </div>
                                        {/* This div represents the second row of the player data column. */}
                                        <div className='flex flex-row justify-center '>
                                            <PlayerData
                                                gamelogData={homeGamelog}
                                                playerHitrates={homePlayerHitrates}
                                                setQueryFilters={setQueryFilters}
                                            />
                                        </div>
                                    </div>
                                )
                                : (
                                    <div>
                                        {/* This div represents the top row of the player data column. */}
                                        <div className='flex flex-none justify-center '>
                                            < PropLines propData={awayPropLines} />
                                        </div>
                                        {/* This div represents the second row of the player data column. */}
                                        <div className='flex flex-row justify-center'>
                                            <PlayerData
                                                gamelogData={awayGamelog}
                                                playerHitrates={awayPlayerHitrates}
                                                setQueryFilters={setQueryFilters}
                                            />
                                        </div>
                                    </div>
                                )
                            }
                        </div>
                    )
                    : (
                        <div className='text-xl'>
                            No Data Available
                        </div>
                    )
                }
                {/* This div contains the matchup data for the selected player with the given filter selection. */}

            </div>
        </div >
    )
}

export default Matchup