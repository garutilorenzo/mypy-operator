% err = error_message if defined('error_message') else ''

% include('header.tpl')
    <main class="container">
        <div class="row justify-content-md-center">
            <div class="col-12  mb-4">
                <div class="bg-light p-5 rounded">
                    <h1>MySql Operator Web interface</h1>
                    <p class="lead">TBD</p>
                    <a class="btn btn-lg btn-primary" href="/docs" role="button">View application docs &raquo;</a>
                </div>
                % if err:
                <div class="alert alert-danger alert-dismissible fade show" role="alert">
                    <strong>Error: </strong> {{ err }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>
                % end
            </div>
        </div>
        % if not err:
        <div class="row justify-content-md-center">
            <div class="col-12  mb-4">
                TBD
            </div>
        </div>
        % end
    </main>
% include('footer.tpl')