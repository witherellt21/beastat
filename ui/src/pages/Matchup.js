import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import MatchupGamelog from '../tables/gamelog/MatchupGamelog';
import PropLines from '../tables/proplines/PropLines';


function Matchup() {
    let { id } = useParams();
    let navigate = useNavigate();

    const [isLoading, setLoading] = useState(true);
    const [matchup, setMatchup] = useState({});
    const [homeAwayToggle, setHomeAwayToggle] = useState(true);

    let loaded = false;

    useEffect(() => {
        axios.get(`http://localhost:3001/matchups/${id}`).then(async (response) => {
            await setMatchup(response.data)
            setLoading(false);
        }).catch((err) => {
            console.log(err);
            return null;
        });
    }, [id, loaded]);

    // if (isLoading) {
    //     return <div className="App">Loading...</div>;
    // }

    return (
        <div>
            {/* <div>
                <div>
                    {matchup.home_player}
                </div>
                <div>
                    {matchup.away_player}
                </div>
            </div> */}
            <div className='flex flex-col w-full'>
                {/* This div contains the buttons for toggling between Player Analyzers */}
                <div className='flex flex-row justify-center h-12 mb-6'>
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
                {/* <button onClick={() => {
                    console.log(matchup)
                }}>Check</button> */}
                {/* {(matchup.homeAwayToggle && matchup.away_player_id) */}
                {!isLoading
                    ? <div className='flex justify-center'>
                        {homeAwayToggle
                            ? < PropLines player_id={matchup.home_player_id} />
                            : <PropLines player_id={matchup.away_player_id} />
                        }
                    </div>
                    : <div>
                        No data to display.
                    </div>
                }
                {/* This div contains the MatchupGamelog for the selected player. */}
                <div className='flex justify-center'>
                    {
                        homeAwayToggle
                            ? <MatchupGamelog matchup_id={id} home_away="home" />
                            : <MatchupGamelog matchup_id={id} home_away="away" />
                    }

                </div>

            </div>
        </div >
    )
}

export default Matchup