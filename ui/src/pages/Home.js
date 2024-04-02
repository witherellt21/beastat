import React from 'react'
import axios from "axios";
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom'


function Home() {
    const [listOfGames, setGames] = useState([]);
    const [isLoading, setIsLoading] = useState(true)
    let navigate = useNavigate();

    useEffect(() => {
        console.log(process.env.REACT_APP_BEASTAT_API_BASE_URL)
        axios.get(`${process.env.REACT_APP_BEASTAT_API_BASE_URL}/matchups/byGame`).then((response) => {
            setGames(response.data);
        });
        setIsLoading(false)
    }, [])



    const get_color_for_defense_rating = (defense_rating) => {
        if (defense_rating <= 4) {
            return 'bg-gradient-to-b from-red-600 to-red-300'
        } else if (defense_rating <= 8) {
            return 'bg-gradient-to-b from-red-400 to-red-200'
        } else if (defense_rating <= 12) {
            return 'bg-gradient-to-b from-red-200 to-white'
        } else if (defense_rating <= 18) {
            return 'bg-gradient-to-b from-gray-300 to-white'
        } else if (defense_rating <= 22) {
            return 'bg-gradient-to-b from-green-200 to-white'
        } else if (defense_rating <= 26) {
            return 'bg-gradient-to-b from-green-400 to-green-200'
        } else if (defense_rating <= 30) {
            return 'bg-gradient-to-b from-green-700 to-green-300'
        }
    }

    return (

        <div className=''>
            {!isLoading && listOfGames?.map((game, key) => {
                return (
                    <div key={key} className='py-4 space-x-2 flex flex-row flex-wrap justify-center items-center'>
                        {/* <span className='flex flex-col justify-center'>{game.time}</span> */}
                        {/* <div className='flex flex-row space-x-0'> */}
                        {/* <div className='space-x-0 bg-red-200'> */}
                        {/* <span className='w-full'>{game.time}</span> */}

                        {/* </div> */}
                        {/* <span className=''>{game.time}</span> */}
                        <div className='w-40 pr-4 flex flex-col space-y-2 justify-center items-end bg-gradient-to-l from-blue-200 via-gray-100 to-white'>
                            <span className='w-full pt-1'>{game.time}</span>

                            <div className='flex flex-row justify-center items-center space-x-2 text-2xl'>
                                <span>
                                    {game.home}
                                </span>
                                <img
                                    src={"https://a.espncdn.com/combiner/i?img=/i/teamlogos/nba/500/" + `${game.home.toLowerCase()}` + ".png&h=60&w=60"}
                                >
                                </img>
                            </div>
                            <div className='flex flex-row justify-center items-center space-x-2 text-2xl'>
                                <span>
                                    {game.away}
                                </span>
                                <img src={"https://a.espncdn.com/combiner/i?img=/i/teamlogos/nba/500/" + `${game.away.toLowerCase()}` + ".png&h=60&w=60"}>
                                </img>
                            </div>
                            {/* <span className='w-full '>{game.spread}</span>
                            <span className='w-full '>{game.time}</span> */}
                            <span className='w-full pb-1'>{game.spread}</span>

                        </div>
                        {/* <span className='w-full'>{game.spread}</span> */}

                        {/* </div> */}
                        {game?.matchups.map((matchup, key) => {
                            return (
                                <button key={key} className=" flex h-48 flex-row relative justify-between items-center w-80 rounded-md bg-gray-400 border-black border-2"
                                    onClick={() => {
                                        navigate(`/matchup/${matchup.id}`)
                                    }}>
                                    <div className='absolute z-40 top-0 left-0 px-2'>
                                        {matchup.position}
                                    </div>
                                    <div className={'relative w-1/2 h-full flex flex-col items-center text-wrap justify-center rounded-l-md ' + `${get_color_for_defense_rating(matchup.away_defense_ranking_overall)}`}>
                                        <div className='absolute top-3 px-2 flex flex-col items-center justify-center '>
                                            < img
                                                src={'http://www.basketball-reference.com/req/202106291/images/headshots/' + `${matchup.home_player.id}` + '.jpg'}
                                                width={55} height={60}
                                                className=''
                                            >
                                            </img>
                                            <div className="title pt-1 text-sm"> {matchup.home_player.name} </div>

                                        </div>
                                        {/* <div className="title"> {matchup.home_player} </div> */}
                                        <div className='absolute bottom-0 w-full flex flex-row space-x-1 px-2 py-1 bg-gray-200 rounded-bl-sm'>
                                            {matchup.away_def_rank_summary?.map((stat_rank, key) => {
                                                return (
                                                    <div key={key} className={'basis-full text-xs border border-black ' + `${get_color_for_defense_rating(stat_rank.value)}`}>
                                                        <div className='w-full'>
                                                            {stat_rank.stat}
                                                        </div>
                                                        <div className='w-full'>
                                                            {stat_rank.value}
                                                        </div>
                                                    </div>
                                                )
                                            })}
                                        </div>
                                    </div>
                                    {/* <div className='flex flex-col justify-center'>
                                    <div className="title"> {value.home_player} </div>
                                    <div className="title"> {value.away_player} </div>
                                </div> */}
                                    <div className='h-full border-l-2 border-black'></div>
                                    {/* <div className={'w-1/2 h-full flex flex-col items-center text-wrap justify-center rounded-r-md ' + `${value.home_defense_ranking > 15
                                    ? 'bg-green-' + `${Math.round((value.home_defense_ranking - 15) / 5) * 100}`
                                    : 'bg-red-' + `${Math.round((15 - value.home_defense_ranking) / 5) * 100}`
                                    }
                                `}> */}
                                    <div className={'relative w-1/2 h-full flex flex-col items-center text-wrap justify-center rounded-r-md ' + `${get_color_for_defense_rating(matchup.home_defense_ranking_overall)}`}>
                                        <div className='absolute top-3 flex flex-col items-center justify-center '>
                                            < img
                                                src={'http://www.basketball-reference.com/req/202106291/images/headshots/' + `${matchup.away_player.id}` + '.jpg'}
                                                width={55} height={60}
                                                className=''
                                            >
                                            </img>
                                            <div className="title pt-1 text-sm"> {matchup.away_player.name} </div>

                                        </div>
                                        <div className='absolute bottom-0 w-full flex flex-row space-x-1 px-2 py-1 bg-gray-200 rounded-br-sm'>
                                            {matchup.home_def_rank_summary?.map((stat_rank, key) => {
                                                return (
                                                    <div key={key} className={'basis-full text-xs border border-black ' + `${get_color_for_defense_rating(stat_rank.value)}`}>
                                                        <div className='w-full'>
                                                            {stat_rank.stat}
                                                        </div>
                                                        <div className='w-full'>
                                                            {stat_rank.value}
                                                        </div>
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    </div>
                                </button>
                            );
                        })}
                    </div >
                );
            })}
        </div>
    )
}

export default Home