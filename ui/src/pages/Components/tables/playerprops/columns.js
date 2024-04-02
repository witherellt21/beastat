import { createColumnHelper } from '@tanstack/react-table';

const columnHelper = createColumnHelper();


export const playerPropsColumns = [
    // columnHelper.group({
    //     header: 'Points',
    //     footer: props => props.column.id,
    //     columns: [
    //         // Accessor Column
    //         columnHelper.accessor('PTS.line', {
    //             cell: info => info.getValue(),
    //             header: () => <span>Line</span>,
    //         }),
    //         columnHelper.accessor('PTS.over_value', {
    //             cell: info => info.getValue(),
    //             header: () => <span>Over</span>,
    //         }),
    //         columnHelper.accessor('PTS.under_value', {
    //             cell: info => info.getValue(),
    //             header: () => <span>Under</span>,
    //         }),
    //     ],
    // }),
    columnHelper.accessor('player.name', {
        cell: info => <button>{info.getValue()}</button>,
        header: () => <span>Player</span>,
    }),
    columnHelper.group({
        header: 'Points',
        footer: props => props.column.id,
        columns: [
            // Accessor Column
            columnHelper.accessor('PTS.line', {
                cell: info => info.getValue(),
                header: () => <span>Line</span>,
            }),
            columnHelper.accessor(row => Math.round(row.PTS?.over_value * 10) / 10, {
                id: 'PTS.over_value',
                cell: info => <span className={`${info.getValue() > 0 ? 'text-green-500' : 'text-red-500'}`}>{info.getValue()}</span>,
                header: () => <span>Over</span>,
            }),
            columnHelper.accessor(row => Math.round(row.PTS?.under_value * 10) / 10, {
                id: 'PTS.under_value',
                cell: info => <span className={`${info.getValue() > 0 ? 'text-green-500' : 'text-red-500'}`}>{info.getValue()}</span>,
                header: () => <span>Under</span>,
            }),
        ],
    }),
    columnHelper.group({
        header: 'Rebounds',
        footer: props => props.column.id,
        columns: [
            // Accessor Column
            columnHelper.accessor('TRB.line', {
                cell: info => info.getValue(),
                header: () => <span>Line</span>,
            }),
            columnHelper.accessor(row => Math.round(row.TRB?.over_value * 10) / 10, {
                id: 'TRB.over_value',
                cell: info => <span className={`${info.getValue() > 0 ? 'text-green-500' : 'text-red-500'}`}>{info.getValue()}</span>,
                header: () => <span>Over</span>,
            }),
            columnHelper.accessor(row => Math.round(row.TRB?.under_value * 10) / 10, {
                id: 'TRB.under_value',
                cell: info => <span className={`${info.getValue() > 0 ? 'text-green-500' : 'text-red-500'}`}>{info.getValue()}</span>,
                header: () => <span>Under</span>,
            }),
        ],
    }),
    columnHelper.group({
        header: 'Assists',
        footer: props => props.column.id,
        columns: [
            // Accessor Column
            columnHelper.accessor('AST.line', {
                cell: info => info.getValue(),
                header: () => <span>Line</span>,
            }),
            columnHelper.accessor(row => Math.round(row.AST?.over_value * 10) / 10, {
                id: 'AST.over_value',
                cell: info => <span className={`${info.getValue() > 0 ? 'text-green-500' : 'text-red-500'}`}>{info.getValue()}</span>,
                header: () => <span>Over</span>,
            }),
            columnHelper.accessor(row => Math.round(row.AST?.under_value * 10) / 10, {
                id: 'AST.under_value',
                cell: info => <span className={`${info.getValue() > 0 ? 'text-green-500' : 'text-red-500'}`}>{info.getValue()}</span>,
                header: () => <span>Under</span>,
            }),
        ],
    }),
    columnHelper.group({
        header: 'Threes',
        footer: props => props.column.id,
        columns: [
            // Accessor Column
            columnHelper.accessor('THP.line', {
                cell: info => info.getValue(),
                header: () => <span>Line</span>,
            }),
            columnHelper.accessor(row => Math.round(row.THP?.over_value * 10) / 10, {
                id: 'THP.over_value',
                cell: info => <span className={`${info.getValue() > 0 ? 'text-green-500' : 'text-red-500'}`}>{info.getValue()}</span>,
                header: () => <span>Over</span>,
            }),
            columnHelper.accessor(row => Math.round(row.THP?.under_value * 10) / 10, {
                id: 'THP.under_value',
                cell: info => <span className={`${info.getValue() > 0 ? 'text-green-500' : 'text-red-500'}`}>{info.getValue()}</span>,
                header: () => <span>Under</span>,
            }),
        ],
    }),
    columnHelper.group({
        header: 'Pts+Reb+Ast',
        footer: props => props.column.id,
        columns: [
            // Accessor Column
            columnHelper.accessor('PRA.line', {
                cell: info => info.getValue(),
                header: () => <span>Line</span>,
            }),
            columnHelper.accessor(row => Math.round(row.PRA?.over_value * 10) / 10, {
                id: 'PRA.over_value',
                cell: info => <span className={`${info.getValue() > 0 ? 'text-green-500' : 'text-red-500'}`}>{info.getValue()}</span>,
                header: () => <span>Over</span>,
            }),
            columnHelper.accessor(row => Math.round(row.PRA?.under_value * 10) / 10, {
                id: 'PRA.under_value',
                cell: info => <span className={`${info.getValue() > 0 ? 'text-green-500' : 'text-red-500'}`}>{info.getValue()}</span>,
                header: () => <span>Under</span>,
            }),
        ],
    }),
    // columnHelper.group({
    //     header: 'Assists',
    //     footer: props => props.column.id,
    //     columns: [
    //         // Accessor Column
    //         columnHelper.accessor('AST.line', {
    //             cell: info => info.getValue(),
    //             header: () => <span>Line</span>,
    //         }),
    //         columnHelper.accessor('AST.over', {
    //             cell: info => info.getValue(),
    //             header: () => <span>Over</span>,
    //         }),
    //         columnHelper.accessor('AST.over_implied', {
    //             cell: info => info.getValue() ? info.getValue() + "%" : "",
    //             header: () => <span>Over</span>,
    //         }),
    //         columnHelper.accessor('AST.under', {
    //             cell: info => info.getValue(),
    //             header: () => <span>Under</span>,
    //         }),
    //         columnHelper.accessor('AST.under_implied', {
    //             cell: info => info.getValue() ? info.getValue() + "%" : "",
    //             header: () => <span>Under</span>,
    //         }),
    //     ],
    // }),
    // columnHelper.group({
    //     header: 'Rebounds',
    //     footer: props => props.column.id,
    //     columns: [
    //         // Accessor Column
    //         columnHelper.accessor('TRB.line', {
    //             cell: info => info.getValue(),
    //             header: () => <span>Line</span>,
    //         }),
    //         columnHelper.accessor('TRB.over', {
    //             cell: info => info.getValue(),
    //             header: () => <span>Over</span>,
    //         }),
    //         columnHelper.accessor('TRB.over_implied', {
    //             cell: info => info.getValue() ? info.getValue() + "%" : "",
    //             header: () => <span>Over</span>,
    //         }),
    //         columnHelper.accessor('TRB.under', {
    //             cell: info => info.getValue(),
    //             header: () => <span>Under</span>,
    //         }),
    //         columnHelper.accessor('TRB.under_implied', {
    //             cell: info => info.getValue() ? info.getValue() + "%" : "",
    //             header: () => <span>Under</span>,
    //         }),
    //     ],
    // }),
    // columnHelper.group({
    //     header: '3PM',
    //     footer: props => props.column.id,
    //     columns: [
    //         // Accessor Column
    //         columnHelper.accessor('THP.line', {
    //             cell: info => info.getValue(),
    //             header: () => <span>Line</span>,
    //         }),
    //         columnHelper.accessor('THP.over', {
    //             cell: info => info.getValue(),
    //             header: () => <span>Over</span>,
    //         }),
    //         columnHelper.accessor('THP.over_implied', {
    //             cell: info => info.getValue() ? info.getValue() + "%" : "",
    //             header: () => <span>Over</span>,
    //         }),
    //         columnHelper.accessor('THP.under', {
    //             cell: info => info.getValue(),
    //             header: () => <span>Under</span>,
    //         }),
    //         columnHelper.accessor('THP.under_implied', {
    //             cell: info => info.getValue() ? info.getValue() + "%" : "",
    //             header: () => <span>Under</span>,
    //         }),
    //     ],
    // }),
    // columnHelper.group({
    //     header: 'PRA',
    //     footer: props => props.column.id,
    //     columns: [
    //         // Accessor Column
    //         columnHelper.accessor('PRA.line', {
    //             cell: info => info.getValue(),
    //             header: () => <span>Line</span>,
    //         }),
    //         columnHelper.accessor('PRA.over', {
    //             cell: info => info.getValue(),
    //             header: () => <span>Over</span>,
    //         }),
    //         columnHelper.accessor('PRA.over_implied', {
    //             cell: info => info.getValue() ? info.getValue() + "%" : "",
    //             header: () => <span>Over</span>,
    //         }),
    //         columnHelper.accessor('PRA.under', {
    //             cell: info => info.getValue(),
    //             header: () => <span>Under</span>,
    //         }),
    //         columnHelper.accessor('PRA.under_implied', {
    //             cell: info => info.getValue() ? info.getValue() + "%" : "",
    //             header: () => <span>Under</span>,
    //         }),
    //     ],
    // }),
    // columnHelper.group({
    //     header: 'PA',
    //     footer: props => props.column.id,
    //     columns: [
    //         // Accessor Column
    //         columnHelper.accessor('PA.line', {
    //             cell: info => info.getValue(),
    //             header: () => <span>Line</span>,
    //         }),
    //         columnHelper.accessor('PA.over', {
    //             cell: info => info.getValue(),
    //             header: () => <span>Over</span>,
    //         }),
    //         columnHelper.accessor('PA.over_implied', {
    //             cell: info => info.getValue() ? info.getValue() + "%" : "",
    //             header: () => <span>Over</span>,
    //         }),
    //         columnHelper.accessor('PA.under', {
    //             cell: info => info.getValue(),
    //             header: () => <span>Under</span>,
    //         }),
    //         columnHelper.accessor('PA.under_implied', {
    //             cell: info => info.getValue() ? info.getValue() + "%" : "",
    //             header: () => <span>Under</span>,
    //         }),
    //     ],
    // }),
    // columnHelper.group({
    //     header: 'PR',
    //     footer: props => props.column.id,
    //     columns: [
    //         // Accessor Column
    //         columnHelper.accessor('PR.line', {
    //             cell: info => info.getValue(),
    //             header: () => <span>Line</span>,
    //         }),
    //         columnHelper.accessor('PR.over', {
    //             cell: info => info.getValue(),
    //             header: () => <span>Over</span>,
    //         }),
    //         columnHelper.accessor('PR.over_implied', {
    //             cell: info => info.getValue() ? info.getValue() + "%" : "",
    //             header: () => <span>Over</span>,
    //         }),
    //         columnHelper.accessor('PR.under', {
    //             cell: info => info.getValue(),
    //             header: () => <span>Under</span>,
    //         }),
    //         columnHelper.accessor('PR.under_implied', {
    //             cell: info => info.getValue() ? info.getValue() + "%" : "",
    //             header: () => <span>Under</span>,
    //         }),
    //     ],
    // }),
    // columnHelper.group({
    //     header: 'RA',
    //     footer: props => props.column.id,
    //     columns: [
    //         // Accessor Column
    //         columnHelper.accessor('RA.line', {
    //             cell: info => info.getValue(),
    //             header: () => <span>Line</span>,
    //         }),
    //         columnHelper.accessor('RA.over', {
    //             cell: info => info.getValue(),
    //             header: () => <span>Over</span>,
    //         }),
    //         columnHelper.accessor('RA.over_implied', {
    //             cell: info => info.getValue() ? info.getValue() + "%" : "",
    //             header: () => <span>Over</span>,
    //         }),
    //         columnHelper.accessor('RA.under', {
    //             cell: info => info.getValue(),
    //             header: () => <span>Under</span>,
    //         }),
    //         columnHelper.accessor('RA.under_implied', {
    //             cell: info => info.getValue() ? info.getValue() + "%" : "",
    //             header: () => <span>Under</span>,
    //         }),
    //     ],
    // }),

]