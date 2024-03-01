import React, { useState, useEffect } from 'react'

import MenuTitle from './MenuTitle';
import Input from '../common/Input.tsx';
import BoundedQueryParam from '../common/BoundedQueryParam.tsx'


function GamesFilters({
    setCurrentQuery,
    currentQuery
}) {
    const [matchupToggle, setMatchupToggle] = useState(currentQuery.matchups_only)
    const [seasonBounds, setSeasonBounds] = useState(currentQuery.date)
    const [resultLimit, setResultLimit] = useState(currentQuery.limit)
    const [marginBounds, setMarginBounds] = useState(currentQuery.margin)
    const [daysRest, setDaysRest] = useState(currentQuery.daysRest)
    const [gameLocation, setGameLocation] = useState(currentQuery.gameLocation)
    const [inStartingLineup, setInStartingLineup] = useState(currentQuery.inStartingLineup)

    useEffect(() => {
        setCurrentQuery({
            ...currentQuery,
            matchups_only: matchupToggle,
            date: seasonBounds,
            limit: resultLimit,
            margin: marginBounds,
            gameLocation: gameLocation,
            daysRest: daysRest,
            inStartingLineup: inStartingLineup
        });


    }, [matchupToggle, resultLimit, marginBounds, seasonBounds, gameLocation, daysRest, inStartingLineup])

    const handleGameLocation = (e) => {
        let value = null
        if (e.target.value != '') {
            value = e.target.value
        }
        setGameLocation(value);
    }

    const handleInStartingLineup = (e) => {
        // let value = null
        // if (e.target.value != '') {
        //     value = e.target.value
        // }
        setInStartingLineup(e.target.value ? Number(e.target.value) : null);
    }

    return (
        <div className='flex flex-col h-full'>
            <MenuTitle title="Filter Game Subset" />
            <div class="flex flex-col w-full h-full p-5 text-black dark:text-gray-200 bg-gray-200">
                <form
                    className="flex flex-col w-full h-full"

                >
                    <div className=" flex flex-col space-y-5">
                        <BoundedQueryParam
                            min_props={{ label: "Starting Season", id: "starting-season" }}
                            max_props={{ label: "Ending Season", id: "ending-season" }}
                            param={currentQuery.date}
                            setParam={setSeasonBounds}
                        />
                        <BoundedQueryParam
                            min_props={{ label: "Margin min", id: "margin-min" }}
                            max_props={{ label: "Margin max", id: "margin-max" }}
                            param={currentQuery.margin}
                            setParam={setMarginBounds}
                        />
                        <BoundedQueryParam
                            min_props={{ label: "Days rest min", id: "days-rest-min" }}
                            max_props={{ label: "Days rest max", id: "days-rest-max" }}
                            param={currentQuery.daysRest}
                            setParam={setDaysRest}
                        />
                        <div className='flex flex-row items-center'>
                            <Input label="Limit" type='number' value={resultLimit} setValue={(e) => setResultLimit(e.target.value)} id="limit-input" />
                            <Input label="Matchups Only" type='checkbox' inline={true} checked={matchupToggle} setValue={(e) => setMatchupToggle(e.target.checked)} />

                            <div className='flex flex-row items-center'>
                                <div className='flex flex-row justify-center items-center space-x-2'>
                                    <label className='text-gray-500 text-xs'>
                                        Game Location
                                    </label>
                                    <select
                                        className='text-sm text-gray-500 rounded-md'
                                        value={gameLocation}
                                        onChange={handleGameLocation}>
                                        <option value={null}>{null}</option>
                                        <option value="home">Home</option>
                                        <option value="away">Away</option>
                                    </select>
                                </div>
                            </div>

                        </div>

                        <div className='flex flex-row items-center'>
                            <div className='flex flex-row justify-center items-center space-x-2'>
                                <label className='text-gray-500 text-xs'>
                                    Starter?
                                </label>
                                <select
                                    className='text-sm text-gray-500 rounded-md'
                                    type="number"
                                    value={inStartingLineup}
                                    onChange={handleInStartingLineup}>
                                    <option value={null}>{null}</option>
                                    <option type="number" value={1}>Yes</option>
                                    <option value={0}>No</option>
                                </select>
                            </div>
                        </div>
                    </div>
                </form>
            </div >
        </div >
    )
}

export default GamesFilters