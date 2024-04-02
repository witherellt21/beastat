import React, { useState } from 'react'
import {
    flexRender,
    useReactTable,
    getCoreRowModel,
    getSortedRowModel,
} from '@tanstack/react-table';
import { playerPropsColumns } from './columns'


function PlayerPropsTable({ playerPropsData }) {

    const [sorting, setSorting] = useState([{
        desc: true,
        id: "PTS.over_value"
    }]);


    const tableInstance = useReactTable({
        columns: playerPropsColumns,
        data: playerPropsData,
        state: {
            sorting,
        },
        getCoreRowModel: getCoreRowModel(),
        getSortedRowModel: getSortedRowModel(),
        debugTable: true,
    })

    return (
        <div className='flex flex-col p-4 justify-center'>
            <h1 className='font-bold text-2xl py-1 bg-blue-200 rounded-t-2xl border-2 border-b-0 border-black'>
                Live Props
            </h1>
            <table className='table-auto'>
                <thead>
                    {tableInstance.getHeaderGroups()?.map((headerElement) => {
                        return <tr key={headerElement.id} className='border-2 border-black'>
                            {headerElement.headers?.map((columnElement) => {
                                return (
                                    <th key={columnElement.id} colSpan={columnElement.colSpan}
                                        className='px-2 border-2 border-black text-xs'
                                    >
                                        <button onClick={() => setSorting([{
                                            desc: true,
                                            id: columnElement.id
                                        }])}>
                                            {
                                                flexRender(
                                                    columnElement.column.columnDef.header,
                                                    columnElement.getContext()
                                                )}
                                        </button>
                                    </th>
                                )
                            })}
                        </tr>
                    })}
                </thead>
                <tbody>
                    {tableInstance.getRowModel().rows?.map((row) => {
                        return (
                            <tr key={row.id}>
                                {row.getVisibleCells()?.map((cell) => {
                                    return <td key={cell.id} className={'border border-gray-300 text-xs ' + `

                                    `}>
                                        <div className='py-1'>
                                            {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                        </div>
                                    </td>;
                                })}
                            </tr>
                        );
                    })}
                </tbody>
                {/* <tfoot>
                    {tableInstance.getFooterGroups()?.map((footerElement) => {
                        return <tr key={footerElement.id} className='border-2 border-black'>
                            {footerElement.headers?.map((columnElement) => {
                                return (
                                    <th key={columnElement.id} colSpan={columnElement.colSpan}
                                        className='px-4 border-2 border-black text-xs'
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
                </tfoot> */}
            </table>
        </div >
    )
}

export default PlayerPropsTable;