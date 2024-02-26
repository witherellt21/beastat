import React, { useState, useEffect } from 'react'

import MenuTitle from './MenuTitle';


function GamesFilters({
    setCurrentQuery,
    currentQuery
}) {
    const [matchupToggle, setMatchupToggle] = useState(currentQuery.matchups_only)
    const [seasonStart, setSeasonStart] = useState(currentQuery.Date)
    const [resultLimit, setResultLimit] = useState(currentQuery.limit)

    useEffect(() => {
        setCurrentQuery({
            ...currentQuery,
            matchups_only: matchupToggle,
            Date: seasonStart,
            limit: resultLimit
        });

    }, [matchupToggle, seasonStart, resultLimit])

    const handleSeasonStart = (e) => {
        setSeasonStart(e.target.value)
    }

    const handleResultLimit = (e) => {
        setResultLimit(e.target.value)
    }

    const handleMatchupToggle = (e) => {
        setMatchupToggle(e.target.checked)
    }

    return (
        <div>
            <MenuTitle title="Filter Game Subset" />
            <div className='space-y-4'>
                <div>
                    <label htmlFor='season-start'>Season Start:</label>
                    <input
                        id='season-start'
                        type='text'
                        value={currentQuery.Date}
                        onChange={handleSeasonStart}
                        className='w-12 mx-1 text-center border border-black rounded-md'
                    />

                </div>
                <div>
                    <label htmlFor="result-limit">Limit Results: </label>
                    <input
                        id="result-limit"
                        type="text"
                        className='w-12 mx-1 text-center border border-black rounded-md'
                        onChange={handleResultLimit}
                        value={currentQuery.limit}
                    >
                    </input>
                </div>
                <div>
                    <label htmlFor="matchup-only-toggle" className="toggle-label text-sm">Current Matchup Only: </label>
                    <input
                        id="matchup-only-toggle"
                        type="checkbox"
                        className="togglecheckbox"
                        onChange={handleMatchupToggle}
                        checked={matchupToggle}
                    >
                    </input>
                </div>
            </div>
        </div>
    )
}

export default GamesFilters