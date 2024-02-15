import React, { useEffect, useState, useMemo } from 'react'
import {
    flexRender,
    useReactTable,
    getCoreRowModel,
} from '@tanstack/react-table';
import axios from 'axios';
import { propLinesColumns } from './columns'


function PropLines(props) {
    const [propData, setPropData] = useState([])
    const [columnVisibility, setColumnVisibility] = React.useState({
        AST_over_implied: false,
        AST_under_implied: false,
        PTS_over_implied: false,
        PTS_under_implied: false,
        THP_over_implied: false,
        THP_under_implied: false,
        TRB_over_implied: false,
        TRB_under_implied: false,
    })

    const tableInstance = useReactTable({
        columns: propLinesColumns,
        data: propData,
        state: {
            columnVisibility,
        },
        onColumnVisibilityChange: setColumnVisibility,
        getCoreRowModel: getCoreRowModel(),
        debugTable: true,
        debugHeaders: true,
        debugColumns: true,

    })


    useEffect(() => {
        axios.get(`http://localhost:3001/player-props/${props.player_id}`)
            .then((response) => {
                setPropData(response.data)
                // console.log(response.data)
            })
            .catch((error) => {
                console.log(error)
            });
        // setPropData({ player_id: props.player_id, ...exampleData })
        // console.log(propData)
    }, [props.player_id]);

    return (
        <div className='flex flex-col justify-center'>
            <h1 className='py-2 font-bold'>
                Prop Lines
            </h1>
            <button onClick={() => {
                console.log(propData)
                console.log(tableInstance.getRowModel())
            }}>Check</button>
            <table className='table-auto'>
                <thead>
                    {tableInstance.getHeaderGroups().map((headerElement) => {
                        return <tr key={headerElement.id}>
                            {headerElement.headers.map((columnElement) => {
                                return (
                                    <th key={columnElement.id} colSpan={columnElement.colSpan}
                                        className='border-2 border-black text-xs px-2'
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
                        console.log(propData)
                        return (
                            <tr key={row.id}>
                                {row.getVisibleCells().map((cell) => {
                                    console.log(cell.column.columnDef.cell)
                                    return <td key={cell.id} className='py-1 border w-16 border-gray-300 text-xs'>
                                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                    </td>;
                                })}
                            </tr>
                        );
                    })}
                </tbody>
            </table>
            <label>
                {/* <input
                    {...{
                        type: 'checkbox',
                        checked: true,
                        onChange: column.getToggleVisibilityHandler(),
                    }}
                />{' '}
                Implied Odds */}
                <button onClick={() =>
                    tableInstance.getAllLeafColumns().map((column) => {
                        if (column.id.endsWith('over') | column.id.endsWith('under')) {
                            console.log(columnVisibility)
                            column.toggleVisibility(!column.getIsVisible())
                        }
                        if (column.id.endsWith('implied')) {
                            console.log(columnVisibility)
                            column.toggleVisibility(!column.getIsVisible())
                        }
                    })
                    // console.log(tableInstance.getAllLeafColumns())
                }>
                    Toggle Visibility
                </button>
            </label>
        </div >
    )
}

export default PropLines;