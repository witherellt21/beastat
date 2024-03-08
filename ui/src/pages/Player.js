import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom';
import axios from 'axios';
import PropLines from './Components/tables/proplines/PropLines';
import PlayerData from './Components/PlayerData';
import PlayerCard from './Components/PlayerCard';
// import { playerPropsColumns } from './Components/tables/playerprops/columns';
import Lineup from './Components/Lineup';

function Player() {
    let { id } = useParams();

    const [player, setPlayer] = useState({});
    const [propLines, setPropLines] = useState({});
    const [seasonAverages, setSeasonAverages] = useState({});
    const [game, setGame] = useState({});
    const [lineups, setLineups] = useState({});


    useEffect(() => {
        axios.get(`${process.env.REACT_APP_BEASTAT_API_BASE_URL}/players/${id}`)
            .then((response) => {
                setPlayer(response.data)
                // setPropLines(response.data)
            })
            .catch((error) => {
                console.log(error)
                return null;
            });
        axios.get(`${process.env.REACT_APP_BEASTAT_API_BASE_URL}/player-props/${id}`)
            .then((response) => {
                setPropLines(response.data)
            })
            .catch((error) => {
                console.log(error)
                return null;
            });

        axios.get(`${process.env.REACT_APP_BEASTAT_API_BASE_URL}/career-stats/${id}/season/2024`)
            .then((response) => {
                setSeasonAverages(response.data)
            })
            .catch((error) => {
                console.log(error)
                return null;
            });


    }, []);

    useEffect(() => {
        axios.get(`${process.env.REACT_APP_BEASTAT_API_BASE_URL}/games/${seasonAverages.Tm}`)
            .then((response) => {
                console.log(response.data)
                setGame(response.data)
                // setSeasonAverages(response.data)
            })
            .catch((error) => {
                console.log(error);
                return null;
            });
    }, [seasonAverages])

    useEffect(() => {
        axios.get(`${process.env.REACT_APP_BEASTAT_API_BASE_URL}/lineups/${game.id}`)
            .then((response) => {
                setLineups(response.data)
            })
            .catch((error) => {
                console.log(error);
                return null;
            });
    }, [game])

    return (
        <div>
            <div className='w-full h-screen flex flex-col'>

                {/* 
                This div contains the all data for the selected player.
                It will only load after the matchup is successfully set.
                */}

                <hr className='my-4'></hr>
                <div className='min-h-44 mb-8 flex flex-row justify-center space-x-8'>
                    <div>
                        <PlayerCard
                            // player_name={matchup.home_player}
                            // player_id={matchup.home_player_id}
                            player={player}
                            position={seasonAverages.Pos}
                            seasonAverages={seasonAverages}
                            team={seasonAverages.Tm}
                        ></PlayerCard>


                    </div>
                    <Lineup
                        lineup={lineups?.home_lineup}
                    ></Lineup>
                    <Lineup
                        lineup={lineups?.away_lineup}
                    ></Lineup>
                </div>
                <div>
                    <div className='flex flex-col justify-center '>
                        <div className='flex flex-none justify-center '>
                            < PropLines propData={propLines} />
                        </div>
                        {/* <StatAveragesTable statAveragesData={}/> */}
                        {/* This div represents the second row of the player data column. */}
                        <div className='flex flex-row justify-center '>
                            <PlayerData
                                player_id={id}
                                defense_rankings={null}
                                team_lineup={lineups?.home_lineup}
                                season_averages={setSeasonAverages}
                            />
                        </div>
                    </div>
                </div>
            </div>

        </div>
    )
}

export default Player