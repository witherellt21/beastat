import React, { useMemo, useEffect, useState, useContext, useReactTable } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
// import { PlayerGame } from "../datatypes/player_game"
import GamelogTable from '../tables/gamelog';

function Matchup() {


    // const columnHelper = createColumnHelper < PlayerGame > ()
    const [homePlayerGamelog, sethomePlayerGamelog] = useState({});
    // // const [mathcupObject, setMatchupObject] = useState({});
    // const table = useReactTable({})

    // const columns = useMemo(
    //     () => [
    //         {
    //             // first group - TV Show
    //             Header: "TV Show",
    //             // First group columns
    //             columns: [
    //                 {
    //                     Header: "Name",
    //                     accessor: "show.name",
    //                 },
    //                 {
    //                     Header: "Type",
    //                     accessor: "show.type",
    //                 },
    //             ],
    //         },
    //         {
    //             // Second group - Details
    //             Header: "Details",
    //             // Second group columns
    //             columns: [
    //                 {
    //                     Header: "Language",
    //                     accessor: "show.language",
    //                 },
    //                 {
    //                     Header: "Genre(s)",
    //                     accessor: "show.genres",
    //                 },
    //                 {
    //                     Header: "Runtime",
    //                     accessor: "show.runtime",
    //                 },
    //                 {
    //                     Header: "Status",
    //                     accessor: "show.status",
    //                 },
    //             ],
    //         },
    //     ],
    //     []
    // );


    let { id } = useParams();
    let navigate = useNavigate();

    useEffect(() => {
        axios.get(`http://localhost:3001/gamelogs/${id}`).then((response) => {
            sethomePlayerGamelog(response.data)
            console.log(response.data)
        });
    }, [id]);

    return (
        <div>
            {/* <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Age</th>
                        <th>Start</th>
                        <th>Minutes Played</th>
                    </tr>
                </thead>
                <tbody>
                    {homePlayerGamelog !== null ? (
                        homePlayerGamelog.map((val, key) => {
                            return (
                                <tr key={key}>
                                    <td>{val.Date}</td>
                                    <td>{val.Age}</td>
                                    <td>{val.GS}</td>
                                    <td>{val.MP}</td>
                                </tr>
                            )
                        })
                    ) : (
                        console.log(homePlayerGamelog)
                        // < tr >
                        //     <td>NaN</td>
                        //     <td>NaN</td>
                        //     <td>NaN</td>
                        //     <td>NaN</td>
                        // </tr>
                    )}
                </tbody>
            </table> */}
            <GamelogTable data={homePlayerGamelog} />
        </div >
    )
}

export default Matchup