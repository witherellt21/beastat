import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import PropLines from './Components/tables/proplines/PropLines';
import PlayerData from './Components/PlayerData';
import PlayerCard from './Components/PlayerCard';
import Lineup from './Components/Lineup';


function Matchup() {
    let { id } = useParams();
    let navigate = useNavigate();

    const [matchupLoaded, setMatchupLoaded] = useState(false);
    const [matchup, setMatchup] = useState({});
    const [homeAwayToggle, setHomeAwayToggle] = useState(true);
    const [homePropLines, setHomePropLines] = useState([]);
    const [awayPropLines, setAwayPropLines] = useState([])
    const [defenseRankings, setDefenseRankings] = useState({})
    const [homePlayerSeasonAverages, setHomePlayerSeasonAverages] = useState({})
    const [awayPlayerSeasonAverages, setAwayPlayerSeasonAverages] = useState({})
    const [lineups, setLineups] = useState({})


    useEffect(() => {
        axios.get(`http://localhost:3001/matchups/${id}`).then(async (response) => {
            setMatchup(response.data)

        }).catch((err) => {
            console.log(err);
            return null;
        });

        setMatchupLoaded(true);

    }, [id]);

    useEffect(() => {

        if (matchupLoaded && matchup != {}) {
            axios.get(`http://localhost:3001/player-props/${matchup?.home_player?.id}`)
                .then((response) => {
                    setHomePropLines(response.data)
                })
                .catch((error) => {
                    console.log(error)
                    return null;
                });
            axios.get(`http://localhost:3001/player-props/${matchup?.away_player?.id}`)
                .then((response) => {
                    setAwayPropLines(response.data)
                })
                .catch((error) => {
                    console.log(error)
                    return null;
                });

            axios.get(`http://localhost:3001/defense-rankings/game/${matchup?.game?.id}/${matchup?.position}`)
                .then((response) => {
                    setDefenseRankings(response.data)
                })
                .catch((error) => {
                    console.log(error)
                    return null;
                });

            axios.get(`http://localhost:3001/career-stats/${matchup?.home_player?.id}/season/2024`)
                .then((response) => {
                    setHomePlayerSeasonAverages(response.data)
                })
                .catch((error) => {
                    console.log(error)
                    return null;
                });
            axios.get(`http://localhost:3001/career-stats/${matchup?.away_player?.id}/season/2024`)
                .then((response) => {
                    setAwayPlayerSeasonAverages(response.data)
                })
                .catch((error) => {
                    console.log(error)
                    return null;
                });

            axios.get(`http://localhost:3001/lineups/${matchup?.game?.id}`)
                .then((response) => {
                    setLineups(response.data)
                })
                .catch((error) => {
                    console.log(error)
                    return null;
                });

        }

    }, [matchup, matchupLoaded])


    return (
        <div>
            <div className='w-full h-screen flex flex-col'>
                {/* This div contains the buttons for toggling between Player Analyzers */}
                <div className='flex flex-row justify-center h-32 min-h-28 mb-6'>
                    {/* Player 1 Selector */}
                    <button
                        className={'flex-1 text-lg hover:bg-gray-200' + `( 
                            ${!homeAwayToggle
                                ? 'bg-gray-100 border-4 border-gray-400 border-opacity-10 hover:bg-gray-200 '
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
                        <div className='flex justify-end'>
                            <div className='w-3/5 flex flex-row justify-between items-center '>
                                <img
                                    src={'http://www.basketball-reference.com/req/202106291/images/headshots/' + `${matchup?.home_player?.id}` + '.jpg'}
                                    width={66} height={60}
                                    className='absolute left-10'
                                >
                                </img>
                                <div>
                                    {matchup?.home_player?.name}
                                </div>
                                <div className='flex pr-2'>
                                    <div className='pr-2'>
                                        Defense OVR Rank:
                                    </div>
                                    {defenseRankings?.away?.OVR}
                                </div>
                            </div>
                        </div>
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
                        <div className='flex justify-left'>
                            <div className='w-3/5 flex flex-row justify-between items-center'>
                                <img
                                    src={'http://www.basketball-reference.com/req/202106291/images/headshots/' + `${matchup?.away_player?.id}` + '.jpg'}
                                    width={60} height={60}
                                    className='absolute right-10'
                                >
                                </img>
                                <div className='flex pl-2'>
                                    <div className='pr-2'>
                                        Defense OVR Rank:
                                    </div>
                                    {defenseRankings?.home?.OVR}
                                </div>
                                <div>
                                    {matchup?.away_player?.name}
                                </div>
                            </div>
                        </div>
                    </button>
                </div>
                {/* 
                This div contains the all data for the selected player.
                It will only load after the matchup is successfully set.
                */}
                <div className='min-h-44 mb-8 flex flex-row justify-center space-x-8'>
                    {homeAwayToggle
                        ? (
                            <PlayerCard
                                // player_name={matchup.home_player}
                                // player_id={matchup.home_player_id}
                                player={matchup?.home_player}
                                position={matchup?.position}
                                seasonAverages={homePlayerSeasonAverages}
                            ></PlayerCard>
                        ) : (
                            <PlayerCard
                                player={matchup?.away_player}
                                position={matchup?.position}
                                seasonAverages={awayPlayerSeasonAverages}
                            ></PlayerCard>
                        )
                    }

                    <Lineup
                        lineup={lineups?.home_lineup}
                    ></Lineup>

                    <Lineup
                        lineup={lineups?.away_lineup}
                    ></Lineup>
                    <button onClick={() => { console.log(lineups) }}>
                        Check lineups
                    </button>


                </div>
                {/* <div>
                    <Lineup></Lineup>
                </div> */}
                {
                    matchupLoaded
                        ? (
                            <div className='flex flex-col justify-center '>
                                {homeAwayToggle
                                    ? (
                                        <div>
                                            {/* This div represents the top row of the player data column. */}
                                            <div className='flex flex-none justify-center '>
                                                < PropLines propData={homePropLines} />
                                            </div>
                                            {/* <StatAveragesTable statAveragesData={}/> */}
                                            {/* This div represents the second row of the player data column. */}
                                            <div className='flex flex-row justify-center '>
                                                <PlayerData
                                                    player_id={matchup?.home_player?.id}
                                                    defense_rankings={defenseRankings?.away}
                                                    team_lineup={lineups?.home_lineup}
                                                    season_averages={homePlayerSeasonAverages}
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
                                                    player_id={matchup?.away_player?.id}
                                                    defense_rankings={defenseRankings?.home}
                                                    team_lineup={lineups?.away_lineup}
                                                    season_averages={awayPlayerSeasonAverages}
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
            </div >
        </div >
    )
}

export default Matchup