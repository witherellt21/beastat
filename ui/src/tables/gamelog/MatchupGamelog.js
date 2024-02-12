import React, { useEffect, useState } from 'react'
import {
    flexRender,
    useReactTable,
    getCoreRowModel,
    getSortedRowModel,
} from '@tanstack/react-table';
import axios from 'axios';
import { columnDef } from './columns'


function MatchupGamelog(props) {

    // let player_id = props.

    const [matchupData, setMatchupData] = useState({});
    const [sorting, setSorting] = useState([{
        desc: false,
        id: "Date"
    }]);

    const tableInstance = useReactTable({
        columns: columnDef,
        data: matchupData,
        state: {
            sorting,
        },
        getCoreRowModel: getCoreRowModel(),
        getSortedRowModel: getSortedRowModel(),
        debugTable: true,
    })


    useEffect(() => {
        axios.get(`http://localhost:3001/matchups/${props.matchup_id}/stats/${props.home_away}`).then((response) => {
            setMatchupData(response.data)
        });
    }, [props.matchup_id, props.home_away]);

    return (
        <div className='flex flex-col justify-center'>
            <h1 className='py-2 font-bold'>
                Matchup Gamelog
            </h1>
            <table className='table-auto'>
                <thead>
                    {tableInstance.getHeaderGroups().map((headerElement) => {
                        return <tr key={headerElement.id} className='border-2 border-black'>
                            {headerElement.headers.map((columnElement) => {
                                return (
                                    <th key={columnElement.id} colSpan={columnElement.colSpan}
                                        className='border-2 border-black text-xs'
                                    >
                                        {
                                            flexRender(
                                                columnElement.column.columnDef.header,
                                                columnElement.getContext()
                                            )}
                                    </th>
                                )
                            })}
                        </tr>
                    })}
                </thead>
                <tbody>
                    {tableInstance.getRowModel().rows.map((row) => {
                        return (
                            <tr key={row.id}>
                                {row.getVisibleCells().map((cell) => {
                                    return <td key={cell.id} className='py-1 border border-gray-300 text-xs'>
                                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                    </td>;
                                })}
                            </tr>
                        );
                    })}
                </tbody>
                <tfoot>
                    {tableInstance.getFooterGroups().map((footerElement) => {
                        return <tr key={footerElement.id} className='border-2 border-black'>
                            {footerElement.headers.map((columnElement) => {
                                return (
                                    <th key={columnElement.id} colSpan={columnElement.colSpan}
                                        className='border-2 border-black text-xs'
                                    >
                                        {
                                            flexRender(
                                                columnElement.column.columnDef.footer,
                                                columnElement.getContext()
                                            )}
                                    </th>
                                )
                            })}
                        </tr>
                    })}
                </tfoot>
            </table>
        </div >
    )
}

export default MatchupGamelog;