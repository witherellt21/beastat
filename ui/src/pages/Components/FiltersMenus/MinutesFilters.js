import React, { useState, useEffect } from 'react'
import MenuTitle from './MenuTitle';
import Input from '../common/Input.tsx';
import BoundedQueryParam from '../common/BoundedQueryParam.tsx';

function MinutesFilters({
    setCurrentQuery,
    currentQuery
}) {
    const [minutesPlayed, setMinutesPlayed] = useState(currentQuery.minutes_played);

    useEffect(() => {
        setCurrentQuery({
            ...currentQuery,
            minutes_played: minutesPlayed
        });

    }, [minutesPlayed])

    return (
        <div className='flex flex-col h-full'>
            <MenuTitle title="Filter Minutes Played" />
            <div className="flex flex-col w-full h-full p-5 text-black dark:text-gray-200 bg-gray-200">
                <form
                    className="flex flex-col w-full h-full"

                >
                    <div className=" flex flex-col space-y-5">
                        <BoundedQueryParam
                            min_props={{ label: "Minutes played (min)", id: "minutes-player-min" }}
                            max_props={{ label: "Minutes played (max)", id: "minutes-player-max" }}
                            param={currentQuery.minutes_played}
                            setParam={setMinutesPlayed}
                        />
                    </div>
                </form>
            </div>
        </div>
    )
}

export default MinutesFilters