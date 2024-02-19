import { createColumnHelper } from '@tanstack/react-table';


const columnHelper = createColumnHelper();

export const columnDef = [
    columnHelper.accessor('player_id', {
        cell: info => info.getValue(),
        header: () => <span>Player ID</span>,
        footer: props => props.column.id,
    }),
    columnHelper.accessor('Date', {
        cell: info => info.getValue(),
        header: () => <span>Date</span>,
        // footer: props => props.column.id,
        footer: "FOOTER"
    }),
    columnHelper.accessor('Tm', {
        cell: info => info.getValue(),
        header: () => <span>Team</span>,
    }),
    columnHelper.accessor('Opp', {
        cell: info => info.getValue(),
        header: () => <span>Opp</span>,
    }),
    columnHelper.accessor('streak', {
        cell: info => info.getValue(),
        header: () => <span>Streak</span>,
    }),
    columnHelper.accessor('GS', {
        cell: info => info.getValue(),
        header: () => <span>GS</span>,
    }),
    columnHelper.accessor('MP', {
        cell: info => info.getValue(),
        header: () => <span>MP</span>,
    }),
    columnHelper.accessor('PTS', {
        cell: info => info.getValue(),
        header: () => <span>PTS</span>,
        // aggregationFn: 'mean',
        // AggregatedCell: ({ cell }) => <div>Team Score: {cell.getValue()}</div>,
        // footer: props => props
    }),
    columnHelper.accessor('AST', {
        cell: info => info.getValue(),
        header: () => <span>AST</span>,
    }),
    columnHelper.accessor('TRB', {
        cell: info => info.getValue(),
        header: () => <span>TRB</span>,
    }),
    columnHelper.accessor('PA', {
        cell: info => info.getValue(),
        header: () => <span>PA</span>,
    }),
    columnHelper.accessor('PR', {
        cell: info => info.getValue(),
        header: () => <span>PR</span>,
    }),
    columnHelper.accessor('RA', {
        cell: info => info.getValue(),
        header: () => <span>RA</span>,
    }),
    columnHelper.accessor('PRA', {
        cell: info => info.getValue(),
        header: () => <span>PRA</span>,
    }),
    columnHelper.accessor('STL', {
        cell: info => info.getValue(),
        header: () => <span>STL</span>,
    }),
    columnHelper.accessor('BLK', {
        cell: info => info.getValue(),
        header: () => <span>BLK</span>,
    }),
    columnHelper.accessor('FG', {
        cell: info => info.getValue(),
        header: () => <span>FG</span>,
    }),
    columnHelper.accessor('FGA', {
        cell: info => info.getValue(),
        header: () => <span>FGA</span>,
    }),
    columnHelper.accessor('THP', {
        cell: info => info.getValue(),
        header: () => <span>3P</span>,
    }),
    columnHelper.accessor('THPA', {
        cell: info => info.getValue(),
        header: () => <span>3PA</span>,
    }),
    columnHelper.accessor('FT', {
        cell: info => info.getValue(),
        header: () => <span>FT</span>,
    }),
    columnHelper.accessor('FTA', {
        cell: info => info.getValue(),
        header: () => <span>FTA</span>,
    }),
    columnHelper.accessor('PF', {
        cell: info => info.getValue(),
        header: () => <span>PF</span>,
    }),

]