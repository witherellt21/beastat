import { createColumnHelper } from '@tanstack/react-table';


const columnHelper = createColumnHelper();

export const columnDef = [
    columnHelper.accessor('Season', {
        id: 'Category',
        cell: info => info.getValue(),
        header: () => <span>Category</span>,
    }),
    columnHelper.accessor('G', {
        cell: info => info.getValue(),
        header: () => <span>G</span>,
    }),
    columnHelper.accessor('GS', {
        cell: info => info.getValue(),
        header: () => <span>GS</span>,
    }),
    columnHelper.accessor(row => Math.round(row.MP * 10) / 10, {
        id: "MP",
        cell: info => info.getValue(),
        header: () => <span>MP</span>,
    }),
    columnHelper.accessor(row => Math.round(row.PTS * 10) / 10, {
        id: "PTS",
        cell: info => info.getValue(),
        header: () => <span>PTS</span>,
        // aggregationFn: 'mean',
        // AggregatedCell: ({ cell }) => <div>Team Score: {cell.getValue()}</div>,
        // footer: props => props
    }),
    columnHelper.accessor(row => Math.round(row.AST * 10) / 10, {
        id: 'AST',
        cell: info => info.getValue(),
        header: () => <span>AST</span>,
    }),
    columnHelper.accessor(row => Math.round(row.TRB * 10) / 10, {
        id: 'TRB',
        cell: info => info.getValue(),
        header: () => <span>TRB</span>,
    }),
    columnHelper.accessor(row => Math.round(row.PA * 10) / 10, {
        id: 'PA',
        cell: info => info.getValue(),
        header: () => <span>PA</span>,
    }),
    columnHelper.accessor(row => Math.round(row.PR * 10) / 10, {
        id: 'PR',
        cell: info => info.getValue(),
        header: () => <span>PR</span>,
    }),
    columnHelper.accessor(row => Math.round(row.RA * 10) / 10, {
        id: 'RA',
        cell: info => info.getValue(),
        header: () => <span>RA</span>,
    }),
    columnHelper.accessor(row => Math.round(row.PRA * 10) / 10, {
        id: 'PRA',
        cell: info => info.getValue(),
        header: () => <span>PRA</span>,
    }),
    columnHelper.accessor(row => Math.round(row.STL * 10) / 10, {
        id: 'STL',
        cell: info => info.getValue(),
        header: () => <span>STL</span>,
    }),
    columnHelper.accessor(row => Math.round(row.BLK * 10) / 10, {
        id: 'BLK',
        cell: info => info.getValue(),
        header: () => <span>BLK</span>,
    }),
    columnHelper.accessor(row => Math.round(row.FG * 10) / 10, {
        id: 'FG',
        cell: info => info.getValue(),
        header: () => <span>FG</span>,
    }),
    columnHelper.accessor(row => Math.round(row.FGA * 10) / 10, {
        id: 'FGA',
        cell: info => info.getValue(),
        header: () => <span>FGA</span>,
    }),
    // columnHelper.accessor(row => Math.round(row.FG_perc * 1000) / 10, {
    //     id: 'FG_perc',
    //     cell: info => info.getValue(),
    //     header: () => <span>FG%</span>,
    // }),
    columnHelper.accessor(row => Math.round(row.FG_perc * 1000) / 10, {
        id: 'FG_perc',
        cell: info => info.getValue(),
        header: () => <span>FG%</span>,
    }),
    columnHelper.accessor(row => Math.round(row.eFG_perc * 1000) / 10, {
        id: 'eFG_perc',
        cell: info => info.getValue(),
        header: () => <span>eFG%</span>,
    }),
    columnHelper.accessor(row => Math.round(row.TWP * 10) / 10, {
        id: 'TWP',
        cell: info => info.getValue(),
        header: () => <span>2P</span>,
    }),
    columnHelper.accessor(row => Math.round(row.TWPA * 10) / 10, {
        id: 'TWPA',
        cell: info => info.getValue(),
        header: () => <span>2PA</span>,
    }),
    columnHelper.accessor(row => Math.round(row.TWP_perc * 1000) / 10, {
        id: 'TWP_perc',
        cell: info => info.getValue(),
        header: () => <span>2P%</span>,
    }),
    columnHelper.accessor(row => Math.round(row.THP * 10) / 10, {
        id: 'THP',
        cell: info => info.getValue(),
        header: () => <span>3P</span>,
    }),
    columnHelper.accessor(row => Math.round(row.THPA * 10) / 10, {
        id: 'THPA',
        cell: info => info.getValue(),
        header: () => <span>3PA</span>,
    }),
    columnHelper.accessor(row => Math.round(row.THP_perc * 1000) / 10, {
        id: 'THP_perc',
        cell: info => info.getValue(),
        header: () => <span>3P%</span>,
    }),
    columnHelper.accessor(row => Math.round(row.FT * 10) / 10, {
        id: 'FT',
        cell: info => info.getValue(),
        header: () => <span>FT</span>,
    }),
    columnHelper.accessor(row => Math.round(row.FTA * 10) / 10, {
        id: 'FTA',
        cell: info => info.getValue(),
        header: () => <span>FTA</span>,
    }),
    columnHelper.accessor(row => Math.round(row.FT_perc * 1000) / 10, {
        id: 'FT_perc',
        cell: info => info.getValue(),
        header: () => <span>FT%</span>,
    }),
    columnHelper.accessor(row => Math.round(row.PF * 10) / 10, {
        id: 'PF',
        cell: info => info.getValue(),
        header: () => <span>PF</span>,
    }),

]