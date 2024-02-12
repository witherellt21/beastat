import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import MatchupGamelog from '../tables/gamelog/MatchupGamelog';
import PropLines from '../tables/proplines/PropLines';


function Matchup() {
    let { id } = useParams();
    let navigate = useNavigate();

    const [matchup, setMatchup] = useState({});
    const [homeAwayToggle, setHomeAwayToggle] = useState(true);

    useEffect(() => {
        axios.get(`http://localhost:3001/matchups/${id}`).then((response) => {
            setMatchup(response.data)
        });
    }, [id]);

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
                <div className='flex flex-row justify-center h-12'>
                    <button
                        className='flex-1 bg-gray-300 hover:bg-gray-400'
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
                        className='flex-1 border-l-2 border-black bg-gray-300 hover:bg-gray-400'
                        onClick={() => {
                            if (homeAwayToggle) {
                                setHomeAwayToggle(false)
                            }
                        }}
                    >
                        {matchup.away_player}
                    </button>
                </div>
                {/* This div contains the MatchupGamelog for the selected player. */}
                <div className='flex justify-center'>
                    {homeAwayToggle
                        ? < PropLines player_id={matchup.home_player_id} />
                        : <PropLines player_id={matchup.away_player_id} />
                    }
                </div>
                {/* This div contains the MatchupGamelog for the selected player. */}
                <div className='flex justify-center'>
                    {homeAwayToggle
                        ? < MatchupGamelog matchup_id={id} home_away="home" />
                        : <MatchupGamelog matchup_id={id} home_away="away" />
                    }
                </div>
            </div>
        </div >
    )
}

export default Matchup