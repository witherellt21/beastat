import React, { useState } from 'react'
import {
    flexRender,
    useReactTable,
    getCoreRowModel,
    getSortedRowModel,
} from '@tanstack/react-table';
import { columnDef } from './columns'


function StatAveragesTable({ statAveragesData }) {

    // const [sorting, setSorting] = useState([{
    //     desc: false,
    //     id: "Date"
    // }]);

    console.log(statAveragesData)

    const tableInstance = useReactTable({
        columns: columnDef,
        data: statAveragesData,
        // state: {
        //     sorting,
        // },
        getCoreRowModel: getCoreRowModel(),
        getSortedRowModel: getSortedRowModel(),
        debugTable: true,
    })

    return (
        // <div className='flex flex-col grow-0 justify-center'>
        <div className='flex flex-col p-4 justify-center'>
            {/* <div className="flex items-center justify-center bg-red-300 rounded-t-2xl border-2 border-b-0 border-black"> */}
            {/* <div className="w-32"> */}
            <h1 className='font-bold text-2xl py-1 bg-blue-200 rounded-t-2xl border-2 border-b-0 border-black'>
                Stat Averages
            </h1>
            {/* </div> */}
            {/* </div > */}
            <table className='table-auto'>
                <thead>
                    {tableInstance.getHeaderGroups().map((headerElement) => {
                        return <tr key={headerElement.id} className='border-2 border-black'>
                            {headerElement.headers.map((columnElement) => {
                                return (
                                    <th key={columnElement.id} colSpan={columnElement.colSpan}
                                        className='px-2 border-2 border-black text-xs'
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
                                    return <td key={cell.id} className='border border-gray-300 text-xs'>
                                        <div className='py-1'>
                                            {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                        </div>
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
                </tfoot>
            </table>
        </div >
    )
}

export default StatAveragesTable;