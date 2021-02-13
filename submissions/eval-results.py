from argparse import ArgumentParser
import logging
import pandas as pd
from sklearn.metrics import f1_score
from sklearn.metrics import accuracy_score


def load_data(file_name, has_header, predictions_column):
    """Reads the predictions and true values from the input file.

    Parameters
    ----------
    file_name: str, required
        The file name containing predictions and true values.
    has_header: boolean, required
        Specifies if the first row of the file is header row.
    predictions_column: int, required
        Specifies the zero-based index of the predictions column.

    Returns
    -------
    (predictions, true_values), tuple of lists representing predictions and true values.
    """
    header = 0 if has_header else None
    logging.info("Reading data from input file {} with header={}.".format(
        file_name, header))
    df = pd.read_csv(file_name, header=header)

    def load_column(df, index, col_type):
        logging.info("Index of {} column is {}.".format(col_type, index))
        col = df.columns[index]
        return df[col].to_list()

    predictions = load_column(df, predictions_column, "predictions")

    true_vals_column = 1 if predictions_column == 0 else 0
    true_values = load_column(df, true_vals_column, "true values")
    return predictions, true_values


def display_results(labels, scores):
    """Prints the scores of each label to console.

    Parameters
    ----------
    labels: list
        The labels for each score.
    scores: list of number
        The list of scores for each label.
    """
    df = pd.DataFrame({'labels': labels, 'scores': scores})
    print(df)


def eval_f1_score(args):
    """Evaluates the F1 score of the predictions from the input file.

    Parameters
    ----------
    args: argparse.Namespace
        The arguments for F1 metric alongside the common arguments.
    """
    logging.info(
        "Evaluating the results from file {} with F1 metric. Average is {}".
        format(args.input_file, args.average))
    predictions, true_values = load_data(args.input_file,
                                         not args.no_header_row,
                                         args.predictions_column)
    labels = list(set(sorted(true_values)))
    scores = f1_score(true_values, predictions, average=args.average)
    display_results(labels, scores)


def eval_accuracy_score(args):
    """Evaluates the accuracy score of the predictions from the input file.

    Parameters
    ----------
    args: argparse.Namespace
        The arguments for accuracy metric alongside the common arguments.
    """
    logging.info(
        "Evaluating the accuracy of predictions from file {}. Show numbers is {}."
        .format(args.input_file, args.show_num_correct))
    predictions, true_values = load_data(args.input_file,
                                         not args.no_header_row,
                                         args.predictions_column)
    score = accuracy_score(true_values,
                           predictions,
                           normalize=not args.show_num_correct)
    print("Accuracy score is: {}.".format(score))


def add_common_arguments(parser):
    """Adds the common arguments to the command-line parser.

    Parameters
    ----------
    parser: argparse.ArgumentParser
        The parser to which to add the arguments.
    """
    parser.add_argument(
        '--input-file',
        help=
        "The name of the input CSV file containing predictions and true labels"
    )
    parser.add_argument(
        '--no-header-row',
        help=
        "When provided, specifies that the input file does not have a header row; i.e. the first row of the file contains predictions and true labels.",
        action='store_true')
    parser.add_argument(
        '--predictions-column',
        help=
        "Zero-based index of the column containing the predictions of the model. Default is 0.",
        type=int,
        default=0)

    parser.add_argument(
        '--log-level',
        help="The level of details to print when running.",
        choices=['debug', 'info', 'warning', 'error', 'critical'],
        default='info')


def parse_arguments():
    root_parser = ArgumentParser()

    subparsers = root_parser.add_subparsers()
    f1 = subparsers.add_parser('f1',
                               help="Compute the F1 score for the input file.")
    f1.set_defaults(func=eval_f1_score)
    add_common_arguments(f1)
    f1.add_argument(
        '--average',
        help="The type of average to perform on the data.",
        choices=['binary', 'micro', 'macro', 'weighted', 'samples'],
        default=None)

    accuracy = subparsers.add_parser(
        'accuracy',
        help='Compute the accuracy of predictions from the input file.')
    accuracy.set_defaults(func=eval_accuracy_score)
    add_common_arguments(accuracy)
    accuracy.add_argument(
        '--show-num-correct',
        action='store_true',
        help=
        "If specified, the score will show the number of correctly classified samples, not the fraction."
    )
    return root_parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                        level=getattr(logging, args.log_level.upper()))
    args.func(args)
    logging.info("Evaluation script finished.")
