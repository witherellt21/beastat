import React, { useState, useEffect } from 'react'
import MenuTitle from './MenuTitle'

function LineupFilters({
    setCurrentQuery,
    currentQuery,
    team_lineup

}) {

    const [withTeammates, setWithTeammates] = useState(currentQuery.withTeammates)
    const [withoutTeammates, setWithoutTeammates] = useState(currentQuery.withoutTeammates)

    useEffect(() => {
        setCurrentQuery({
            ...currentQuery,
            withTeammates: withTeammates,
            withoutTeammates: withoutTeammates
        });

    }, [withTeammates, withoutTeammates])

    const toggleTeammateIncluded = (player) => {
        let array = [...withTeammates]
        const index = array.indexOf(player);
        if (index > -1) { // only splice array when item is found
            array.splice(index, 1); // 2nd parameter means remove one item only
        } else {
            array = [...array, player]
        }
        setWithTeammates(array)
    }

    const toggleTeammateExcluded = (player) => {
        let array = [...withoutTeammates]
        const index = array.indexOf(player);
        if (index > -1) { // only splice array when item is found
            array.splice(index, 1); // 2nd parameter means remove one item only
        } else {
            array = [...array, player]
        }
        setWithoutTeammates(array)
    }

    return (
        <div>
            <MenuTitle title="Filter By Lineup" />
            <div className='flex flex-col'>
                <span className='pl-2 text-left text-sm'>Games With Teammates:</span>
                <span className='w-full py-1 border-t border-gray-300'></span>
                <div className='flex flex-row justify-center'>
                    <div className='flex flex-col items-start'>
                        <div>
                            <input
                                type='checkbox'
                                id='PG_included'
                                onChange={(e) => {
                                    toggleTeammateIncluded(team_lineup?.PG)
                                }}
                                checked={withTeammates.includes(team_lineup?.PG)}
                            ></input>
                            <label className="pl-2" htmlFor='PG_included'>{team_lineup?.PG}</label>
                        </div>
                        <div>
                            <input
                                type='checkbox'
                                id='SG_included'
                                onChange={(e) => {
                                    toggleTeammateIncluded(team_lineup?.SG)
                                }}
                                checked={withTeammates.includes(team_lineup?.SG)}
                            ></input>
                            <label className="pl-2" htmlFor='SG_included'>{team_lineup?.SG}</label>
                        </div>
                        <div>
                            <input
                                type='checkbox'
                                id='SF_included'
                                onChange={(e) => {
                                    toggleTeammateIncluded(team_lineup?.SF)
                                }}
                                checked={withTeammates.includes(team_lineup?.SF)}
                            ></input>
                            <label className="pl-2" htmlFor='SF_included'>{team_lineup?.SF}</label>
                        </div>
                        <div>
                            <input
                                type='checkbox'
                                id='PF_included'
                                onChange={(e) => {
                                    toggleTeammateIncluded(team_lineup?.PF)
                                }}
                                checked={withTeammates.includes(team_lineup?.PF)}
                            ></input>
                            <label className="pl-2" htmlFor='PF_included'>{team_lineup?.PF}</label>
                        </div>
                        <div>
                            <input
                                type='checkbox'
                                id='C_included'
                                onChange={(e) => {
                                    toggleTeammateIncluded(team_lineup?.C)
                                }}
                                checked={withTeammates.includes(team_lineup?.C)}
                            ></input>
                            <label className="pl-2" htmlFor='C_included'>{team_lineup?.C}</label>
                        </div>
                    </div>
                </div>
                <span className='pl-2 mt-4 text-left text-sm'>Games Without Teammates:</span>
                <span className='w-full py-1 border-t border-gray-300'></span>
                <div className='flex flex-row justify-center'>
                    <div className='flex flex-col items-start'>
                        {team_lineup?.injuries.map((injured_player, key) => {
                            return (
                                <div key={key}>
                                    <input
                                        type='checkbox'
                                        id={`${key}_included`}
                                        onChange={(e) => {
                                            toggleTeammateExcluded(injured_player.player_name)
                                        }}
                                        checked={withoutTeammates.includes(injured_player.player_name)}
                                    ></input>
                                    <label className="pl-2" htmlFor={`${key}_included`}>{injured_player.player_name}</label>
                                    {/* {value.player_name} */}
                                </div>
                            )
                        })}
                    </div>
                </div>
            </div>
        </div>
    )
}

export default LineupFilters