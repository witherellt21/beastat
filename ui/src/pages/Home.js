import React from 'react'
import axios from "axios";
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom'


function Home() {
    const [listOfMatchups, setMatchups] = useState([]);
    const [isLoading, setIsLoading] = useState(true)
    let navigate = useNavigate();

    useEffect(() => {
        axios.get("http://192.168.183.216:3001/matchups/").then((response) => {
            setMatchups(response.data);
        });
        setIsLoading(false)
    }, [])

    // useEffect(() => {

    // }, [listOfMatchups])

    const get_color_for_defense_rating = (defense_rating) => {
        if (defense_rating <= 4) {
            return 'bg-red-600'
        } else if (defense_rating <= 8) {
            return 'bg-red-400'
        } else if (defense_rating <= 12) {
            return 'bg-red-200'
        } else if (defense_rating <= 18) {
            return 'bg-gray-300'
        } else if (defense_rating <= 22) {
            return 'bg-green-400'
        } else if (defense_rating <= 26) {
            return 'bg-green-600'
        } else if (defense_rating <= 30) {
            return 'bg-green-600'
        }
    }

    return (
        <div className='flex flex-row flex-wrap justify-center'>
            {!isLoading && listOfMatchups.map((value, key) => {
                return (
                    <button key={key} className="h-36 flex flex-row relative justify-between items-center w-80 rounded-md bg-gray-400 m-2 border-black border-2"
                        onClick={() => {
                            navigate(`/matchup/${value.id}`)
                        }}>
                        <div className='absolute top-0 left-0 px-2'>
                            {value.position}
                        </div>
                        {/* <div className={'w-1/2 h-full flex flex-col items-center text-wrap justify-center rounded-l-md ' + `${value.away_defense_ranking > 15
                            ? 'bg-green-' + `${Math.round((value.away_defense_ranking - 15) / 5) * 100}`
                            : 'bg-red-' + `${Math.round((15 - value.away_defense_ranking) / 5) * 100}`
                            }
                        `}> */}
                        {/* <div className={'w-1/2 h-full flex flex-col items-center text-wrap justify-center rounded-l-md ' + `${value.away_defense_ranking > 15
                            ? 'bg-green-' + `${Math.round((value.away_defense_ranking - 15) / 5) * 100}`
                            : 'bg-red-' + `${Math.round((15 - value.away_defense_ranking) / 5) * 100}`
                            }
                        `}> */}
                        <div className={'w-1/2 h-full flex flex-col items-center text-wrap justify-center rounded-l-md ' + `${get_color_for_defense_rating(value.away_defense_ranking)}`}>
                            {/* <div className='w-1/2 flex flex-col items-center text-wrap justify-center' style={{ backgroundColor: 'blue', opacity: 0.3 }}> */}
                            <div className='mt-2 flex justify-center space-x-2'>
                                < img
                                    src={'http://www.basketball-reference.com/req/202106291/images/headshots/' + `${value.home_player_id}` + '.jpg'}
                                    width={55} height={60}
                                    className=''
                                >
                                </img>
                                {/* <div className='flex flex-col px-2 bg-gray-200'>
                                    <div className='text-xs'>
                                        Data
                                    </div>
                                </div> */}
                            </div>
                            <div className="title"> {value.home_player} </div>
                            {/* <div>
                                {value.away_defense_ranking}
                            </div> */}
                            <div className='flex flex-row px-2 bg-gray-200'>
                                <div className='text-xs'>
                                    Data
                                </div>
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
                        <div className={'w-1/2 h-full flex flex-col items-center text-wrap justify-center rounded-l-md ' + `${get_color_for_defense_rating(value.home_defense_ranking)}`}>
                            <img
                                src={'http://www.basketball-reference.com/req/202106291/images/headshots/' + `${value.away_player_id}` + '.jpg'}
                                width={55}
                                className='mt-2'
                            >
                            </img>
                            <div className="title"> {value.away_player} </div>
                            <div>
                                {value.home_defense_ranking}
                            </div>
                        </div>
                    </button>);
            })}
        </div >
    )
}

export default Home